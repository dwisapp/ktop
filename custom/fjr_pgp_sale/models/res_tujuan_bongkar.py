from odoo import models, fields, api, _

class ResTujuanBongkar(models.Model):
    _name = 'res.tujuan.bongkar'
    _description = 'Tujuan Bongkar'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)