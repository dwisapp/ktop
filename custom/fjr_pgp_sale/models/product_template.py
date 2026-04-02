from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    delivery_note_ok = fields.Boolean(string='Can be Delivery Note', default=False)