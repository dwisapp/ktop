from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    expense_whatsapp_approval_template = fields.Many2one('whatsapp.template', 'Expense Approval Template', domain="[('model_id.model', '=', 'hr.expense.sheet')]")
    expense_whatsapp_send_money_template = fields.Many2one('whatsapp.template', 'Expense Send Money Template', domain="[('model_id.model', '=', 'hr.expense.sheet')]")


    journal_settlement_expense_id = fields.Many2one("account.journal", "Journal Settlement Expense")
