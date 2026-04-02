from odoo import models, fields, api, _

class FleetItemUsage(models.Model):
    _name = 'fleet.item.usage'
    _description = "Item Usage for Fleet"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Usage Number', required=True, copy=False,  index=True, default=lambda self: _('New'))
    fleet_id = fields.Many2one('fleet.vehicle', string='Fleet', required=True)
    date = fields.Datetime("Date", default=fields.Datetime.now, required=True)
    usage_type = fields.Selection([
        ('loan', _('Loan')),
        ('usage', _('Usage')),
    ], string='Usage Type', default='usage', required=True)
    
    state = fields.Selection([
        ('draft', _('Draft')),
        ('in_loan', _('In Loan')),
        ('used', _('Used')),
        ('return', _('Return')),
        ('lost', _('Lost')),
        ('cancel', _('Cancel')),
    ], string='Status', default='draft', copy=False, tracking=True)

    description = fields.Html("Description")
    usage_move_ids = fields.One2many('stock.move', 'fleet_item_usage_id', string='Usage Moves')
    return_move_ids = fields.One2many('stock.move', 'fleet_item_return_id', string='Return Moves')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    location_id = fields.Many2one('stock.location', string='Item Location', required=True, domain="[('fleet_usage_location', '=', True)]")
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', related="company_id.fleet_usage_location")
    display_button_return = fields.Boolean("Display Button Return", compute='_compute_display_button_return')

    @api.depends('usage_move_ids', 'usage_move_ids.returned_qty')
    def _compute_display_button_return(self):
        for rec in self:
            rec.display_button_return = rec.usage_type == 'loan' and any([move.quantity_to_return > 0 for move in rec.usage_move_ids])


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.item.usage') or _('New')
        return super(FleetItemUsage, self).create(vals)
    

    def action_confirm(self):
        for rec in self:
            if rec.usage_type == 'loan':
                rec.state = 'in_loan'
            else:
                rec.state = 'used'
            rec.usage_move_ids.write({'is_inventory': True, 'picked': True,})
            for move in rec.usage_move_ids:
                move.write({'quantity':move.product_uom_qty, 'origin': rec.name})
            rec.usage_move_ids.with_context(inventory_mode=False)._action_done(cancel_backorder=True)

    def action_return(self):
        return {
            'name': _('Return Fleet Item Usage'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.return.fleet.item.usage',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_fleet_item_usage_id': self.id,
                'default_line_ids': [(0, 0, {
                    'product_id': move.product_id.id,
                    'origin_move_id': move.id,
                    'quantity_used': move.quantity - move.returned_qty,
                    'quantity_return': move.quantity - move.returned_qty,
                }) for move in self.usage_move_ids.filtered(lambda x: x.quantity_to_return > 0)]}
        }

  

    def action_cancel(self):
        self.write({'state': 'cancel'})
        self.usage_move_ids.action_move_cancel()        

    
   
    
    