from odoo import models, fields, api, _
from odoo.osv import expression

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    employee_structur_type_id = fields.Many2one('hr.payroll.structure.type', string='Specific Payroll Structure Type')
    

    @api.depends('employee_structur_type_id')
    def _compute_employee_ids(self):
        super(HrPayslipEmployees, self)._compute_employee_ids()

    def _get_available_contracts_domain(self):
        domain = super(HrPayslipEmployees, self)._get_available_contracts_domain()
        if self.employee_structur_type_id:
            domain = expression.AND([
                domain,
                [('contract_ids.structure_type_id', '=', self.employee_structur_type_id.id)]
            ])
        return domain