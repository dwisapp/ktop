from odoo import models, fields, api, _


class HrEmployee(models.AbstractModel):
    _inherit = 'hr.employee.base'

    employee_payroll_bank_id = fields.Many2one(
        'res.bank',
        string='Payroll Bank Account',
        help="This bank account will be used for payroll payment.",
    )
    employee_payroll_bank_acc_number = fields.Char(
        string='Payroll Bank Account Number',
        help="This bank account number will be used for payroll payment.",
    )

    