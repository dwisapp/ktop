from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby

class FleetVehicleLogService(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _rec_name = 'name'

    purchase_line_ids = fields.One2many("purchase.order.line", "vehicle_service_id", string="Purchase Order Line")
    active_purchase = fields.Boolean(string='Active Purchase', compute='_compute_active_purchase', search='_search_active_purchase')
    service_part_ids = fields.One2many('fleet.vehicle.log.services.part', 'vehicle_service_id', string='Purchase Parts')
    location_id = fields.Many2one('stock.location', string='Location', domain="[('fleet_usage_location', '=', True)]")
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', related="company_id.fleet_usage_location")
    stock_move_ids = fields.One2many('stock.move', 'fleet_vehicle_log_service_id', string='Stock Moves')
    use_stock = fields.Boolean("Use Stock ?")
    date = fields.Datetime("Date", default=fields.Datetime.now, required=True)
    amount = fields.Monetary(compute="_compute_total_cost",  store=True)
    name = fields.Char("Service Number", copy=False,  index=True, default=lambda self: _('New'))



    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.stock_move_ids.write({'location_id': self.location_id.id})

    @api.depends('purchase_line_ids.price_total','stock_move_ids')
    def _compute_total_cost(self):
        for service in self:
            service.amount = sum(service.service_part_ids.mapped('purchase_line_ids.price_total')) + sum(service.stock_move_ids.stock_valuation_layer_ids.mapped('value'))
    

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.vehicle.log.services') or _('New')
        return super(FleetVehicleLogService, self).create(vals)


    @api.depends('purchase_line_ids')
    def _compute_active_purchase(self):
        for service in self:
            service.active_purchase = any(line.state != 'cancel' and line.product_qty > 0 for line in service.purchase_line_ids)


    def _search_active_purchase(self, operator, value):
        if operator == '=':
            if value:
                return [('purchase_line_ids.state', '!=', 'cancel'), ('purchase_line_ids.product_qty', '>', 0)]
            else:
                return ['|', '|', ('purchase_line_ids.state', '=', 'cancel'), ('purchase_line_ids.product_qty', '=', 0), ('purchase_line_ids', '=', False)]
        else:
            if value:
                return ['|','|', ('purchase_line_ids.state', '=', 'cancel'), ('purchase_line_ids.product_qty', '=', 0), ('purchase_line_ids', '=', False)]
            else:
                return [('purchase_line_ids.state', '!=', 'cancel'), ('purchase_line_ids.product_qty', '>', 0)]

    def create_purchase_order(self):
        no_vendor_self = self.filtered(lambda r: not r.vendor_id)
        if no_vendor_self:
            raise UserError(_('Please set a vendor on the following services: %s', ', '.join(no_vendor_self.mapped('service_type_id.name'))))
        cancel_self = self.filtered(lambda r: r.state == 'cancel')
        if cancel_self:
            raise UserError(_('You cannot create a purchase order for a cancelled service: %s', ', '.join(cancel_self.mapped('service_type_id.name'))))
        
        no_product_self = self.filtered(lambda r: not r.service_part_ids)
        if no_product_self:
            raise UserError(_('Please set a product on the following services: %s', ', '.join(no_product_self.mapped('service_type_id.name'))))

        purchase_order = self.env['purchase.order']
        for vendor_id, services in groupby(self, lambda r: r.vendor_id):
            services_obj = self.env['fleet.vehicle.log.services']
            order_line_vals = []
            for service in services:
                services_obj |= service
                # if not service.service_type_id.product_id:
                #     service.service_type_id.product_id = self.env['product.product'].create({
                #         'name': service.service_type_id.name,
                #         'type': 'service',
                #     })

                for line in service.service_part_ids:
                    order_line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': f"{line.product_id.name} {service.vehicle_id.name} {service.description}",
                        'product_qty': 1,
                        'product_uom': line.product_id.uom_id.id,
                        # 'price_unit': service.amount,
                        'vehicle_id': service.vehicle_id.id,
                        'vehicle_service_id': service.id,
                        'vehicle_service_part_id': line.id,
                    }))
            order_vals = {
                'partner_id': vendor_id.id,
                'order_line': order_line_vals,
                # 'vehicle_service_id': self.id,
            }
            purchase = self.env['purchase.order'].create(order_vals)
            
            purchase_order |= purchase

        if purchase_order:
            action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
            if len(purchase_order) > 1:
                action['domain'] = [('id', 'in', purchase_order.ids)]
            else:
                action['res_id'] = purchase_order.id
                action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            return action
        
    
    def action_view_purchase_order(self):
        purchase_order = self.purchase_line_ids.order_id
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        if len(purchase_order) > 1:
            action['domain'] = [('id', 'in', purchase_order.ids)]
        else:
            action['res_id'] = purchase_order.id
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        return action

    def unlink(self):
        self_with_purchase = self.filtered(lambda r: r.active_purchase)

        if self_with_purchase:
            raise UserError(_('You cannot delete a service that has a purchase order related to it.'))
        return super(FleetVehicleLogService, self).unlink()
    
    def write(self, vals):
        if 'state' in vals:
            if vals['state'] == 'done':
                if self.stock_move_ids:
                    self.stock_move_ids.write({'is_inventory': True, 'picked': True,})
                    for move in self.stock_move_ids:
                        move.write({'quantity':move.product_uom_qty, 'origin': f"Service - {self.vehicle_id.name} - {self.description}"})
                    self.stock_move_ids.with_context(inventory_mode=False)._action_done(cancel_backorder=True)
            elif vals['state'] == 'cencelled':
                if self.stock_move_ids:
                    self.stock_move_ids.action_move_cancel()
                self_with_purchase = self.filtered(lambda r: r.active_purchase)
                if self_with_purchase:
                    raise UserError(_('You cannot cancel a service that has a purchase order related to it. Please cancel the purchase order first.'))
            elif vals['state'] in ['new', 'running']:
                done_moves = self.stock_move_ids.filtered(lambda x: x.state == 'done')
                cancel_moves = self.stock_move_ids.filtered(lambda x: x.state == 'cancel')
                done_cancel_moves = done_moves + cancel_moves
                if done_cancel_moves:
                    done_moves.action_move_cancel()
                    done_cancel_moves.sudo().write({'state': 'draft'})
                    done_cancel_moves.move_line_ids.sudo().write({'state': 'draft'})
        return super(FleetVehicleLogService, self).write(vals)

class FleetVehicleLogServicePart(models.Model):
    _name = 'fleet.vehicle.log.services.part'
    _description = 'Fleet Vehicle Log Services Part'

    vehicle_service_id = fields.Many2one('fleet.vehicle.log.services', string='Vehicle Service')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity')
    purchase_line_ids = fields.One2many("purchase.order.line", "vehicle_service_part_id", string="Purchase Order Line")