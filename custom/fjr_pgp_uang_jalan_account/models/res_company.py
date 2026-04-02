from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_uang_jalan_id = fields.Many2one('account.account', string='Uang Jalan Account', domain="[('deprecated', '=', False)]")
    journal_uang_jalan_id = fields.Many2one('account.journal', string='Uang Jalan Journal')