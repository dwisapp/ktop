from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_transporter = fields.Boolean(string='Is Transporter', default=False)
    driver_delivery_note_ids = fields.One2many('delivery.note', 'transporter_id', string='Delivery Notes as Driver')