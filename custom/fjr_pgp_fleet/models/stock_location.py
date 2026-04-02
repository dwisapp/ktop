from odoo import models, fields, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    fleet_usage_location = fields.Boolean(string='Fleet Item Usage Location', default=False)