from odoo import models, fields, api, _

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    settlement_expense_id = fields.Many2one("hr.expense.settlement", "Settlement Expense")

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        
        res['settlement_expense_id'] = self.settlement_expense_id.id
        return res