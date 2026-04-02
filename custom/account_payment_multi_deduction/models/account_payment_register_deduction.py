from odoo import models, fields, api, _

class AccountPaymentRegisterDeduction(models.Model):
    _name = "account.payment.register.deduction"
    _description = "Payment Deduction"


    name = fields.Char(string="Label", required=True)
    active = fields.Boolean(string="Active", default=True)
    line_ids = fields.One2many(
        comodel_name="account.payment.register.deduction.line",
        inverse_name="deduction_id",
        string="Deduction Lines",
        copy=True,
    )

class AccountPaymentRegisterDeductionLine(models.Model):
    _name = "account.payment.register.deduction.line"
    _description = "Payment Deduction Line"

    name = fields.Char(string="Description")
    deduction_id = fields.Many2one('account.payment.register.deduction', string='Deduction')
    account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False)], required=True)
    amount_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], string='Amount Type', required=True, default='percentage')
    amount = fields.Float(string='Amount')
    before_taxes = fields.Boolean(string='Before Taxes', default=False)
