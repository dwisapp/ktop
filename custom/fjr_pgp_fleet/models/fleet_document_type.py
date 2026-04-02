from odoo import models, fields, api, _

class FleetDocumentType(models.Model):
    _name = 'fleet.document.type'
    _description = "Document Type for Fleet"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)