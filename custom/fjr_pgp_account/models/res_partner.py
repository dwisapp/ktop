from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'


    invoice_sequence_id = fields.Many2one('ir.sequence', string='Invoice Sequence', help="This field contains the information about the sequence of the invoice.")
    use_specific_invoice_sequence = fields.Boolean(string='Use Specific Invoice Sequence', help="If this field is checked, the system will use the specific invoice sequence for this partner.")