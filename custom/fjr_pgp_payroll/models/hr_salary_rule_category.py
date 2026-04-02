from odoo import models, fields, api, _


class HrSalaryRuleCategory(models.Model):
    _order = 'sequence, id'
    _inherit = 'hr.salary.rule.category'


    sequence = fields.Integer(string='Sequence')
    display_in_payslip = fields.Boolean(string='Display in Payslip', default=True)
