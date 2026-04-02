from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    uang_jalan_id = fields.Many2one('uang.jalan', string='Uang Jalan')