from odoo import models, fields, api,_

class UangJalanCategory(models.Model):
    _name = 'uang.jalan.category'


    name = fields.Char(string='Nama Kategori Uang Jalan', required=True)