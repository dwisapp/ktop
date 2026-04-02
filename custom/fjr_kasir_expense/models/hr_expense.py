from odoo import models, fields, api, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    state = fields.Selection(selection=[
            ('draft', 'To Report'),
            ('reported', 'To Submit'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved By Manager'),
            ('approved_accounting', 'Approved By Accounting'),
            ('approved_accounting_manager', 'Approved By Accounting Manager'),
            ('in_payment', 'In Payment'),
            ('done', 'Done'),
            ('refused', 'Refused')
        ])
    payment_mode = fields.Selection(default='company_account')
    
    settlement_id = fields.Many2one("hr.expense.settlement", "Settlement", copy=False)
    accounting_id = fields.Many2one('res.users', 'Accounting', copy=False, domain=lambda self: [('groups_id', 'in', self.env.ref('fjr_kasir_expense.group_hr_expense_accounting_user').id)])
    accounting_manager_id = fields.Many2one('res.users', 'Accounting Manager', copy=False, domain=lambda self: [('groups_id', 'in', self.env.ref('fjr_kasir_expense.group_hr_expense_accounting_manager').id)])
    manager_id = fields.Many2one(
        comodel_name='res.users',
        string="Manager",
        compute='_compute_from_employee_id', store=True, readonly=False,
        domain=lambda self: [('groups_id', 'in', self.env.ref('hr_expense.group_hr_expense_team_approver').id)],
        copy=False,
        tracking=True,
    )

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for expense in self:
            expense.manager_id = expense.employee_id.expense_manager_id or expense.employee_id.parent_id.user_id


    @api.depends('sheet_id', 'sheet_id.account_move_ids', 'sheet_id.state')
    def _compute_state(self):
        super(HrExpense, self)._compute_state()
        for expense in self:
            if expense.sheet_id.state == 'approved_accounting':
                expense.state = 'approved_accounting'
            elif expense.sheet_id.state == 'approved_accounting_manager':
                expense.state = 'approved_accounting_manager'
            elif expense.sheet_id.state in ('in_payment', 'failed'):
                expense.state = 'in_payment'


    def _get_default_expense_sheet_values(self):
        values = super(HrExpense, self)._get_default_expense_sheet_values()
        for val in values:
            val["description"] = val["name"]
            val['name'] = "New"
        return values