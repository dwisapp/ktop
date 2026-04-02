from odoo import models, fields, api, _

class UangJalanJenisBarang(models.Model):
    _name = 'uang.jalan.jenis.barang'

    name = fields.Char(string='Nama Jenis Barang', required=True)