from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_state = fields.Selection(selection_add=[('failed', 'Failed')])
    settlement_expense_id = fields.Many2one("hr.expense.settlement", "Settlement Expense", copy=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def action_register_payment(self):
        action = super(AccountMoveLine, self).action_register_payment()
        settlement_expense_id = self._context.get('settlement_expense_id', False)
        if settlement_expense_id:
            action['context']['default_settlement_expense_id'] = settlement_expense_id


        return action