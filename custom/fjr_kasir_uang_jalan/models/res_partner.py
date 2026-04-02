from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # uang_jalan_ids = fields.One2many('uang.jalan', 'driver_id', string='Uang Jalan')