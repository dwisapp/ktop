from odoo import models, fields, api, _


class MidtransPayoutLog(models.Model):
    _name = 'midtrans.payout.log'
    _description = 'Midtrans Payout Log'


    res_id = fields.Char(string='Record ID')
    reference_no = fields.Char(string='Reference No')
    model_name = fields.Char(string='Model Name' , store=True)