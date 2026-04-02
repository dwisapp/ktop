from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    fleet_usage_loan = fields.Boolean(string='Fleet Usage Loan')
    fleet_usage = fields.Boolean(string='Fleet Usage')