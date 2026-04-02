from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_draft(self):

        res = super(AccountPayment, self).action_draft()
        self_with_settlement = self.filtered(lambda p: p.settlement_expense_id)
        self_with_settlement.settlement_expense_id.recompute_payment_state()
        return res
    
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        self_with_settlement = self.filtered(lambda p: p.settlement_expense_id)
        self_with_settlement.settlement_expense_id.recompute_payment_state()
        return res