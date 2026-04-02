from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    fleet_item_usage_id = fields.Many2one('fleet.item.usage', string='Fleet Item Usage')
    fleet_item_return_id = fields.Many2one('fleet.item.usage', string='Fleet Item Return')
    fleet_vehicle_log_service_id = fields.Many2one('fleet.vehicle.log.services', string='Vehicle Service')
    stock_move_usage_id = fields.Many2one('stock.move', string='Stock Move Usage')
    stock_move_return_ids = fields.One2many('stock.move', 'stock_move_usage_id', string='Stock Move Return')
    returned_qty = fields.Float(string='Returned Quantity', compute='_compute_returned_qty', store=True)
    quantity_to_return = fields.Float(string='Quantity to Return', compute='_compute_quantity_to_return')

    fleet_item_usage_status = fields.Selection(related='fleet_item_usage_id.state', string='Usage Status')

    @api.depends('quantity', 'returned_qty')
    def _compute_quantity_to_return(self):
        for rec in self:
            rec.quantity_to_return = rec.quantity - rec.returned_qty

    @api.depends('stock_move_return_ids.state', 'stock_move_return_ids.quantity')
    def _compute_returned_qty(self):
        for rec in self:
            rec.returned_qty = sum(rec.stock_move_return_ids.filtered(lambda x: x.state == 'done').mapped('quantity'))


    def _check_stock_account_installed(self):
        stock_account_app = self.env['ir.module.module'].sudo().search([('name','=','stock_account')],limit=1)
        if stock_account_app.state != 'installed':
            return False
        else:
            return True

    def action_move_cancel(self):
        for rec in self:
            rec.sudo().write({'state': 'cancel'})
            rec.mapped('move_line_ids').sudo().write({'state': 'cancel'})
            rec._force_unreserved_qty()

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(['|',('credit_move_id','in',reconcile_ids),('debit_move_id','in',reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped('line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state':'draft','name':'/'})
                account_move.sudo().with_context({'force_delete':True}).unlink()
            
                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()


    def _force_unreserved_qty(self):
        for move_line in self.sudo().mapped('move_line_ids'):
            # unreserve qty
            quant_source = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                        ('product_id', '=',
                                                            move_line.product_id.id),
                                                        ('lot_id', '=', move_line.lot_id.id)], limit=1)
            quant_dest = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                        ('product_id', '=',
                                                            move_line.product_id.id),
                                                        ('lot_id', '=', move_line.lot_id.id)], limit=1)
            if move_line.state == 'done':

                if quant_source:
                    quant_source.write({'quantity': quant_source.quantity + move_line.quantity})
                else:
                    self.env['stock.quant'].sudo().create({
                        'product_id': move_line.product_id.id,
                        'location_id': move_line.location_id.id,
                        'quantity': move_line.quantity,
                        'lot_id': move_line.lot_id.id,
                    })


                if quant_dest:
                    quant_dest.write({'quantity': quant_dest.quantity - move_line.quantity})
                else:
                    self.env['stock.quant'].sudo().create({
                        'product_id': move_line.product_id.id,
                        'location_id': move_line.location_dest_id.id,
                        'quantity': -move_line.quantity,
                        'lot_id': move_line.lot_id.id,
                    })


            elif move_line.state != 'cancel':
                move_line.move_id._do_unreserve()

    def action_open_fleet_usage(self):
        action = self.env['ir.actions.act_window']._for_xml_id('fjr_pgp_fleet.fleet_item_usage_action')
        action['res_id'] = self.fleet_item_usage_id.id
        action['view_mode'] = 'form'
        action['views'] = [(self.env.ref('fjr_pgp_fleet.fleet_item_usage_view_form').id, 'form')]
        
        return action