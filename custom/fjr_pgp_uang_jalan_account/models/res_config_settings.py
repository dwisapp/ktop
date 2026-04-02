from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_uang_jalan_id = fields.Many2one('account.account', related='company_id.account_uang_jalan_id', string='Uang Jalan Account', domain="[('deprecated', '=', False)]",readonly=False)
    journal_uang_jalan_id = fields.Many2one('account.journal', related='company_id.journal_uang_jalan_id', string='Uang Jalan Journal',readonly=False)