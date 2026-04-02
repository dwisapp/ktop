from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrPaymentPerDelivery(models.Model):
    _name = 'hr.payment.per.delivery'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    tempat_muat_id = fields.Many2one("res.tempat.muat", string="Tempat Muat", ondelete="restrict")
    active = fields.Boolean(string='Active', default=True)
    tujuan_bongkar_id = fields.Many2one("res.tujuan.bongkar", string="Tujuan Bongkar", ondelete="restrict")
    vehicle_category_id = fields.Many2one('fleet.vehicle.model.category', string='Vehicle Category', ondelete="restrict")
    amount = fields.Float(string='Amount')

    
    @api.depends('tempat_muat_id', 'tujuan_bongkar_id', 'vehicle_category_id')
    def _compute_display_name(self):
        super(HrPaymentPerDelivery, self)._compute_display_name()
        for rec in self:
            rec.display_name = f'{rec.tempat_muat_id.name} - {rec.tujuan_bongkar_id.name} - {rec.vehicle_category_id.name}'

    @api.constrains('tempat_muat_id', 'tujuan_bongkar_id', 'vehicle_category_id')
    def _check_unique(self):
        for rec in self:
            if self.env['hr.payment.per.delivery'].search_count([('tempat_muat_id', '=', rec.tempat_muat_id.id), ('tujuan_bongkar_id', '=', rec.tujuan_bongkar_id.id), ('vehicle_category_id', '=', rec.vehicle_category_id.id)]) > 1:
                raise UserError(_('Tempat Muat, Tujuan Bongkar, and Vehicle Category must be unique!'))