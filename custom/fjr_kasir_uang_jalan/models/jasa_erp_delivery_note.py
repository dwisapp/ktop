# from odoo import models, fields, api, _

# class JasaErpDeliveryNote(models.Model):
#     _inherit = 'jasa.erp.delivery.note'

#     uang_jalan_ids = fields.One2many('uang.jalan', 'jasa_erp_delivery_note_id', string='Uang Jalan')
#     uang_jalan_count = fields.Integer(string='Uang Jalan Count', compute='_compute_uang_jalan_count')

#     @api.depends('uang_jalan_ids')
#     def _compute_uang_jalan_count(self):
#         for rec in self:
#             rec.uang_jalan_count = len(rec.uang_jalan_ids)

#     def action_view_uang_jalan(self):
#         self.ensure_one()
#         return {
#             'name': _('Uang Jalan'),
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'uang.jalan',
#             'domain': [('jasa_erp_delivery_note_id', '=', self.id)],
#         }
        
    
#     def action_create_uang_jalan(self):
#         self.ensure_one()
#         return {
#             'name': _('Create Uang Jalan'),
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'uang.jalan',
#             'context': {
#                 'default_jasa_erp_delivery_note_id': self.id,
#                 'default_driver_id': self.driver_id.id,
#                 'default_fleet_id': self.fleet_id.id,
#             }
#         }
