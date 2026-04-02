from odoo import models, fields, api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings' 


    expense_whatsapp_approval_template = fields.Many2one('whatsapp.template', 'Expense Approval Template', domain="[('model_id.model', '=', 'hr.expense.sheet')]", related='company_id.expense_whatsapp_approval_template', readonly=False)
    expense_whatsapp_send_money_template = fields.Many2one('whatsapp.template', 'Expense Send Money Template', domain="[('model_id.model', '=', 'hr.expense.sheet')]", related='company_id.expense_whatsapp_send_money_template', readonly=False)

    journal_settlement_expense_id = fields.Many2one("account.journal", "Journal Settlement Expense", related='company_id.journal_settlement_expense_id', readonly=False)