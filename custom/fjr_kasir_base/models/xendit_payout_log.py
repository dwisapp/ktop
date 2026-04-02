from odoo import models, fields, api, _


class XenditPayoutLog(models.Model):
    _name = 'xendit.payout.log'
    _description = 'Xendit Payout Log'


    res_id = fields.Char(string='Record ID')
    reference_no = fields.Char(string='Reference No')
    model_name = fields.Char(string='Model Name' , store=True)
    amount = fields.Float(string='Amount')

