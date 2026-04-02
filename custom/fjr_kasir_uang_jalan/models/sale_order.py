from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    uang_jalan_ids = fields.One2many('uang.jalan', 'sale_order_id', string='Uang Jalan')
    rute_uang_jalan_id = fields.Many2one('rute.uang.jalan', string='Rute')

    

    @api.onchange('rute_uang_jalan_id')
    def _onchange_rute_uang_jalan_id(self):
        self.write({
            'tempat_muat': self.rute_uang_jalan_id.tempat_muat,
            'tujuan_bongkar': self.rute_uang_jalan_id.tujuan_bongkar,
        })