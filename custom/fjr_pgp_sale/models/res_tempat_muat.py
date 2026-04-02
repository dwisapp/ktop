from odoo import models, fields, api, _

class ResTempatMuat(models.Model):
    _name = 'res.tempat.muat'
    _description = 'Tempat Muat'


    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)