from odoo import models, fields, api, _

class AccountPaymentMethodLine(models.Model):
    _inherit = 'account.payment.method.line'

    is_internal_transfer = fields.Boolean(string='Internal Transfer?', default=False, help="If this field is checked, the system will use this payment method line for internal transfer.")