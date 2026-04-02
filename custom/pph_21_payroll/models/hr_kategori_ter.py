from odoo import models, fields, api

class HrKategoriTER(models.Model):
    _name = 'hr.kategori.ter'

    name = fields.Char(string='Name', required=True)
