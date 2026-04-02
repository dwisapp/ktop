from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_driver = fields.Boolean(string="Driver?")
    # nik = fields.Char(string="NIK")
    # no_rekening = fields.Char(string='No. Rekening')
    # bank_account_name = fields.Char(string='Bank Account Name')