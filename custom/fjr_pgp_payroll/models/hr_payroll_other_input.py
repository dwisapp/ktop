from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class HrPayrollOtherInput(models.Model):
    _name = 'hr.payroll.other.input'
    _description = 'HR Payroll Input'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char("Description", required=True)
    input_type_id = fields.Many2one('hr.payslip.input.type', string='Input Type', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary('Amount', required=True, tracking=True)
  
    start_date = fields.Date('Start Date', tracking=True)
    end_date = fields.Date('End Date', tracking=True)
    decreased_every_month = fields.Boolean('Decreased Every Month', tracking=True)
    
    input_mode = fields.Selection([('employee', 'By Employee'), ('company', 'By Company'),
                                   ('department', 'By Department'),('category', 'By Employee Tags')],
                                   string='Mode', required=True, default='employee')
    employee_ids = fields.Many2many('hr.employee', string='Employees', tracking=True)
    department_ids = fields.Many2many('hr.department', string='Departments', tracking=True)
    category_ids = fields.Many2many('hr.employee.category', string='Employee Tags', tracking=True)

    input_line_ids = fields.One2many('hr.payroll.other.input.line', 'input_id', string='Input Lines', compute='_compute_input_line_ids', store=True, readonly=False)
    employee_to_input = fields.Many2many('hr.employee', relation='hr_employee_input_hr_payroll_other_input_rel', column1='input_id', column2='employee_id', string='Employee to Input') 

    state = fields.Selection([
        ('draft', _('Draft')),
        ('confirm', _('Confirmed')),
        ('cancel', _('Cancelled')),
    ], string='Status', default='draft', tracking=True, readonly=True)

    hr_payslip_input_ids = fields.Many2many('hr.payslip.input', 'hr_payslip_input_hr_payroll_other_input_rel', 'other_input_id', 'hr_payslip_input_id', string='Payslip Inputs')



    @api.depends('amount', 'decreased_every_month', 'start_date', 'end_date')
    def _compute_input_line_ids(self):
        for input in self:
            input.input_line_ids = [(5, 0, 0)]
            if not input.decreased_every_month:
                continue
            if not input.start_date or not input.end_date:
                continue
            
            input_line_vals = []
            difference = relativedelta(input.end_date, input.start_date)
            total_months = (difference.years * 12) + difference.months + 1
            amount = input.amount / total_months
            for i in range(total_months):
                date_start = input.start_date + relativedelta(months=i)
                date_start = max(date_start.replace(day=1), input.start_date)
                input_line_vals.append((0, 0, input._preprae_input_line_vals(amount, date_start)))
            input.input_line_ids = input_line_vals

    



    def action_confirm(self):
        not_draft_state = self.filtered(lambda x: x.state != 'draft')
        if not_draft_state:
            raise UserError(_('Only draft inputs can be confirmed.'))

        for input in self:
            employee_ids = self.env['hr.employee']
            if input.input_mode == 'employee':
                employee_ids = input.employee_ids
            elif input.input_mode == 'department':
                employee_ids = self.env['hr.employee'].search([('department_id', 'in', input.department_ids.ids)])
            elif input.input_mode == 'category':
                employee_ids = self.env['hr.employee'].search([('category_ids', 'in', input.category_ids.ids)])
            elif input.input_mode == 'company':
                employee_ids = self.env['hr.employee'].search([('company_id', '=', input.company_id.id)])
            if not employee_ids:
                raise UserError(_('No employees selected!'))
            input.employee_to_input = [(6, 0, employee_ids.ids)]
            
        self.write({'state': 'confirm'})   

    def action_cancel(self):
        if self.hr_payslip_input_ids.payslip_id:
            raise UserError(_('You cannot cancel an input that is already used in a payslip.'))

        self.write({'state': 'cancel','employee_to_input': [(5, 0, 0)]})

    def action_draft(self):
        if self.hr_payslip_input_ids.payslip_id:
            raise UserError(_('You cannot cancel an input that is already used in a payslip.'))
        self.write({'state': 'draft','employee_to_input': [(5, 0, 0)]})


    def action_view_payslip(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_payroll.action_view_hr_payslip_form')
        action['domain'] = [('id', 'in', self.hr_payslip_input_ids.payslip_id.ids)]

        return action



    def unlink(self):
        for input in self:
            if input.state != 'draft':
                raise UserError(_('You cannot delete confirmed inputs.'))
        return super(HrPayrollOtherInput, self).unlink()

    


    def _preprae_input_line_vals(self, amount, date):
        return {
            'amount': amount,
            'date': date,
        }
    
    

   
class HRPayrollOtherInputLine(models.Model):
    _name = 'hr.payroll.other.input.line'
    _description = 'HR Payroll Input Line'


    input_id = fields.Many2one('hr.payroll.other.input', string='Input', ondelete='cascade')
    date = fields.Date('Date')
    amount = fields.Monetary('Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='input_id.currency_id')


    def write(self, vals):
        res = super(HRPayrollOtherInputLine, self).write(vals)
        if 'amount' in vals:
            for line in self:
                line.input_id.amount = sum(line.input_id.input_line_ids.mapped('amount'))
        return res