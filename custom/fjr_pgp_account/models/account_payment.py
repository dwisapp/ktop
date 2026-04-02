from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    @api.depends('available_payment_method_line_ids', 'is_internal_transfer')
    def _compute_payment_method_line_id(self):
        super(AccountPayment, self)._compute_payment_method_line_id()
        for pay in self.filtered(lambda pay: pay.is_internal_transfer):
            available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(lambda line: line.is_internal_transfer)
            if available_payment_method_line_ids:
                pay.payment_method_line_id = available_payment_method_line_ids[0]._origin

    
   