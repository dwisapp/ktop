from odoo import models, fields, api, _

class RuteUangJalan(models.Model):
    _name = 'rute.uang.jalan'
    _description = 'Rute Uang Jalan'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name', required=True)
    tempat_muat = fields.Char(string='Tempat Muat')
    tujuan_bongkar = fields.Char(string='Tujuan Bongkar')
    amount = fields.Monetary(string='Nominal Uang Jalan')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    