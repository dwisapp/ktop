from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'



    advance_expense = fields.Boolean(string='Advance Expense', default=False)