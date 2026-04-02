from odoo import models, fields, api, _

class DeliveryNote(models.Model):
    _inherit = 'delivery.note'

    uang_jalan_ids = fields.One2many('uang.jalan', 'delivery_notes_id', string='Uang Jalan')
    uang_jalan_count = fields.Integer(string='Uang Jalan Count', compute='_compute_uang_jalan_count')

    @api.depends('uang_jalan_ids')
    def _compute_uang_jalan_count(self):
        for rec in self:
            rec.uang_jalan_count = len(rec.uang_jalan_ids)

    def action_view_uang_jalan(self):
        self.ensure_one()
        return {
            'name': _('Uang Jalan'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'uang.jalan',
            'domain': [('delivery_notes_id', '=', self.id)],
        }
        
    
    def action_create_uang_jalan(self):
        self.ensure_one()
        sale_order_id = self.line_ids.mapped('sale_line_id.order_id')
        if sale_order_id and len(sale_order_id) == 1:
            sale_order_id = sale_order_id.id
        elif sale_order_id and len(sale_order_id) > 1:
            sale_order_id = sale_order_id[0].id
        
        
        return {
            'name': _('Create Uang Jalan'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'uang.jalan',
            'context': {
                'default_delivery_notes_id': self.id,
                'default_driver_employee_id': self.driver_employee_id.id,
                'default_fleet_id': self.fleet_id.id,
            }
        }
