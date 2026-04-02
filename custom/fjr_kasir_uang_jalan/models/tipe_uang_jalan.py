from odoo import models, fields, api, _

class TipeUangJalan(models.Model):
    _name = 'tipe.uang.jalan'
    _description = 'Tipe Uang Jalan'


    name = fields.Char(string='Nama Tipe Uang Jalan', required=True)