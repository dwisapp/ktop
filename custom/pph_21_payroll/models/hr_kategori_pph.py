from odoo import models, fields

class HrKategoriPph(models.Model):
    _name = 'hr.kategori.pph'

    name = fields.Char(string='Name', required=True)
    hr_kategori_ter_id = fields.Many2one('hr.kategori.ter', string='Kategori TER', required=True)