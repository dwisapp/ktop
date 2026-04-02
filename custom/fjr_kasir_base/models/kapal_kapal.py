from odoo import models, fields, api, _

class KapalKapal(models.Model):
    _name = 'kapal.kapal'
    _description = 'Daftar Kapal'

    name = fields.Char(string='Nama Kapal', required=True)