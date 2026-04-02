from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import pytz
from datetime import datetime, time
from odoo.addons.resource.models.utils import make_aware
from collections import defaultdict
import math





class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    sum_worked_days = fields.Float(string='Sum of Worked Days', compute='_compute_sum_worked_days', store=True)
    sum_payment_per_delivery = fields.Float(string='Sum of Payment Per Delivery', compute='_compute_sum_payment_per_delivery', store=True)
    payment_per_delivery_ids = fields.One2many('hr.payslip.payment.per.delivery', 'payslip_id', string='Payment Per Delivery')
    use_delivery_note = fields.Boolean(related='struct_id.use_delivery_note', string='Use Delivery Note')
    is_subsidi_driver = fields.Boolean('Subsidi', compute='_compute_is_subsidi_driver', store=True, readonly=False)
    nominal_subsidi_driver = fields.Float('Nominal Subsidi Driver', compute='_compute_is_subsidi_driver', store=True, readonly=False)
    employee_bank_id = fields.Many2one('res.bank', string='Employee Bank', compute='_compute_employee_bank_id', store=True)

    @api.depends('employee_id')
    def _compute_employee_bank_id(self):
        for payslip in self:
            payslip.employee_bank_id = payslip.employee_id.bank_account_id.bank_id

    @api.depends('contract_id')
    def _compute_is_subsidi_driver(self):
        for payslip in self:
            payslip.is_subsidi_driver = payslip.contract_id.subsidi_driver
            payslip.nominal_subsidi_driver = payslip.contract_id.nominal_subsidi_driver



    @api.depends('payment_per_delivery_ids.amount')
    def _compute_sum_payment_per_delivery(self):
        for payslip in self:
            payslip.sum_payment_per_delivery = sum(payslip.payment_per_delivery_ids.mapped('amount'))


    @api.depends('worked_days_line_ids.number_of_days')
    def _compute_sum_worked_days(self):
        for payslip in self:
            payslip.sum_worked_days = sum(payslip.worked_days_line_ids.mapped('number_of_days'))

    def compute_sheet(self):
        payslips = self.filtered(lambda slip: slip.state in ['draft', 'verify'])

        payslip_with_delivery_notes = payslips.filtered(lambda slip: slip.struct_id.use_delivery_note)
        payslip_with_delivery_notes.payment_per_delivery_ids.unlink()
        if not payslips:
            return super(HrPayslip, self).compute_sheet()
        # delete old payslip lines
        payslips.input_line_ids.filtered(lambda line: line.payroll_other_input_ids).unlink()
        self.env.flush_all()
        payslip_date_from = min(payslips.mapped('date_from'))
        payslip_date_to = max(payslips.mapped('date_to'))

        


        other_input_domain = [
            '|',
            '|',
            '|',
            '&',('start_date', '=', False),('end_date', '=', False),
            '&',('start_date','=',False),('end_date','>=',payslip_date_from),
            '&',('start_date','<=',payslip_date_to),('end_date','=',False),
            '&',('start_date','<=',payslip_date_to),('end_date','>=',payslip_date_from),
            ('employee_to_input', 'in', payslips.employee_id.ids),
            ('state', '=', 'confirm'),
        ]

        delivery_note_domain =  [
            ('state', '=', 'complete'),
            ('delivery_finish_date','<=',payslip_date_to),('delivery_finish_date','>=',payslip_date_from),
            ('driver_employee_id', 'in', payslip_with_delivery_notes.employee_id.ids),
        ]


        other_inputs = self.env['hr.payroll.other.input'].search(other_input_domain)

        delivery_notes = self.env['delivery.note'].read_group(delivery_note_domain, ['driver_employee_id', 'tempat_muat_id','tujuan_bongkar_id','vehicle_category_id','__count' ], ['driver_employee_id', 'tempat_muat_id','tujuan_bongkar_id','vehicle_category_id',], lazy=False)
        payment_per_delivery = self.env['hr.payment.per.delivery'].search([])


        for payslip in payslips:
            matched_other_inputs = other_inputs.filtered(lambda input:  ( not input.start_date and not input.end_date) \
                                                         or (not input.start_date and input.end_date >= payslip.date_from) \
                                                            or (input.start_date <= payslip.date_to and not input.end_date) \
                                                            or (input.start_date <= payslip.date_to and input.end_date >= payslip.date_from))
            
            
            matched_employee = matched_other_inputs.filtered(lambda input: payslip.employee_id in input.employee_to_input)
            input_by_code = {}
            for input in matched_employee:
                if input.input_type_id.code not in input_by_code:
                    input_by_code[input.input_type_id.code] = payslip._prepare_input_line_vals(payslip.date_to, input)
                else:
                    added_input = payslip._prepare_input_line_vals(payslip.date_to, input)
                    input_by_code[input.input_type_id.code]['amount'] += added_input['amount']
                    input_by_code[input.input_type_id.code]['name'] += ', ' + added_input['name']
                    input_by_code[input.input_type_id.code]['payroll_other_input_ids'] += added_input['payroll_other_input_ids']

            payslip.write({'input_line_ids': [(0, 0, input) for input in input_by_code.values()]})

            payment_per_delivery_dict = defaultdict(lambda: 0)
            if payslip.struct_id.use_delivery_note:
                for dn in delivery_notes:
                    if dn['driver_employee_id'] and dn['tempat_muat_id'] and dn['tujuan_bongkar_id'] and dn['vehicle_category_id']:
                        if dn['driver_employee_id'][0] == payslip.employee_id.id:
                            same_payment_config = payment_per_delivery.filtered(lambda ppd: ppd.tempat_muat_id.id == dn['tempat_muat_id'][0] and ppd.tujuan_bongkar_id.id == dn['tujuan_bongkar_id'][0] and ppd.vehicle_category_id.id == dn['vehicle_category_id'][0])
                            if same_payment_config:
                                payment_per_delivery_dict[same_payment_config] += dn['__count']
            for ppd_id, quantity in payment_per_delivery_dict.items():
                payslip.payment_per_delivery_ids = [(0, 0, {
                    'payment_per_delivery_id': ppd_id.id,
                    'quantity': quantity,
                    'amount': ppd_id.amount,
                })]
        


        # for payslip in same_payslip:
        #     matched_employee = other_inputs.filtered(lambda input: payslip.employee_id in input.employee_to_input)
        #     input_by_code = {}
        #     for input in matched_employee:
        #         if input.code not in input_by_code:
        #             input_by_code[input.code] = payslip._prepare_input_line_vals(payslip.date_to, input)
        #         else:
        #             added_input = payslip._prepare_input_line_vals(payslip.date_to, input)
        #             input_by_code[input.code]['amount'] += added_input['amount']
        #             input_by_code[input.code]['name'] += ', ' + added_input['name']
        #             input_by_code[input.code]['payroll_other_input_ids'] += added_input['payroll_other_input_ids']

        #     payslip.write({'input_line_ids': [(0, 0, input) for input in input_by_code.values()]})

        return super(HrPayslip, self).compute_sheet()


    def _prepare_input_line_vals(self, date, payroll_other_input_id):
        amount = payroll_other_input_id.amount
        if payroll_other_input_id.decreased_every_month:
            amount = payroll_other_input_id.input_line_ids.filtered(lambda line: line.date <= date)[-1].amount

        return {
            'amount': amount,
            'name': payroll_other_input_id.name,
            'payroll_other_input_ids': [payroll_other_input_id.id],
            'input_type_id': payroll_other_input_id.input_type_id.id,
        }
    

    
    @api.depends('contract_id')
    def _compute_struct_id(self):
        super(HrPayslip, self)._compute_struct_id()
        for slip in self.filtered(lambda p: p.contract_id.payroll_structure_id):
            slip.struct_id = slip.contract_id.payroll_structure_id.id
        

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        result = super(HrPayslip, self)._get_worked_day_lines(domain=domain, check_out_of_contract=check_out_of_contract)
        slip_tz = pytz.timezone(self.contract_id.resource_calendar_id.tz)
        utc = pytz.timezone('UTC')
        date_from = slip_tz.localize(datetime.combine(self.date_from, time.min)).astimezone(utc)
        date_to = slip_tz.localize(datetime.combine(self.date_to, time.max)).astimezone(utc)

        
        overtime_leaves = self.contract_id.resource_calendar_id._leave_intervals_batch(date_from, date_to,resources=self.employee_id.resource_id,domain=[('time_type', '=', 'other')])[self.employee_id.resource_id.id]
        overtimes = {}
        for start, stop, leave in overtime_leaves:
            if not overtimes.get(leave.work_entry_type_id.id):
                overtimes[leave.work_entry_type_id.id] = {
                    'sequence': leave.work_entry_type_id.sequence,
                    'number_of_hours': 0,
                    'work_entry_type_id': leave.work_entry_type_id.id,
                    'number_of_days': 0,
                    'is_credit_time': True,
                }
            hours = (stop - start).total_seconds() / 3600
            overtimes[leave.work_entry_type_id.id]['number_of_hours'] += hours
            overtimes[leave.work_entry_type_id.id]['number_of_days'] += 1

        result += list(overtimes.values())
        return result



    def _get_salary_rule_in_print_payslip(self):
        payslip_line_by_categ = defaultdict(lambda: self.env['hr.payslip.line'])
        for line in self.line_ids:
            if line.salary_rule_id.category_id.display_in_payslip:
                payslip_line_by_categ[line.salary_rule_id.category_id] |= line
        return payslip_line_by_categ
    

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        if not self.struct_id.rule_ids.filtered(lambda r: r.code == "NET").account_credit.reconcile:
            raise UserError(_('The credit account on the NET salary rule is not reconciliable'))
        
        return self.move_id.with_context(
            default_partner_id=self.employee_id.work_contact_id.id,
        ).action_register_payment()


    def action_print_payslip_excel(self):
        return {
            'name': 'Payslip',
            'type': 'ir.actions.act_url',
            'url': '/print/payslips-excel?list_ids=%(list_ids)s' % {'list_ids': ','.join(str(x) for x in self.ids)},
        }


    def _get_period_name(self, cache):
        self.ensure_one()
        period_name = '%s - %s' % (
            self._format_date_cached(cache, self.date_from),
            self._format_date_cached(cache, self.date_to))
        if self.is_wrong_duration:
            return period_name

        start_date = self.date_from
        end_date = self.date_to
        lang = self.employee_id.lang or self.env.user.lang
        week_start = self.env["res.lang"]._lang_get(lang).week_start
        schedule = self.contract_id.schedule_pay or self.contract_id.structure_type_id.default_schedule_pay
        if schedule == 'monthly':
            period_name = self._format_date_cached(cache, end_date, "MMMM Y")
        elif schedule == 'quarterly':
            current_year_quarter = math.ceil(start_date.month / 3)
            period_name = _("Quarter %s of %s", current_year_quarter, start_date.year)
        elif schedule == 'semi-annually':
            year_half = start_date.replace(day=1, month=6)
            is_first_half = start_date < year_half
            period_name = _("1st semester of %s", start_date.year)\
                if is_first_half\
                else _("2nd semester of %s", start_date.year)
        elif schedule == 'annually':
            period_name = start_date.year
        elif schedule == 'weekly':
            wk_num = start_date.strftime('%U') if week_start == '7' else start_date.strftime('%W')
            period_name = _('Week %(week_number)s of %(year)s', week_number=wk_num, year=start_date.year)
        elif schedule == 'bi-weekly':
            week = int(start_date.strftime("%U") if week_start == '7' else start_date.strftime("%W"))
            first_week = week - 1 + week % 2
            period_name = _("Weeks %(week)s and %(week1)s of %(year)s",
                week=first_week, week1=first_week + 1, year=start_date.year)
        elif schedule == 'bi-monthly':
            start_date_string = self._format_date_cached(cache, start_date, "MMMM Y")
            end_date_string = self._format_date_cached(cache, end_date, "MMMM Y")
            period_name = _("%s and %s", start_date_string, end_date_string)
        return period_name


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    payroll_other_input_ids = fields.Many2many('hr.payroll.other.input', 'hr_payslip_input_hr_payroll_other_input_rel', 'hr_payslip_input_id', 'other_input_id',string='Payslip Inputs')


class HrPayslipPaymentPerDelivery(models.Model):
    _name = 'hr.payslip.payment.per.delivery'


    payslip_id = fields.Many2one('hr.payslip', string='Payslip', ondelete='cascade')
    payment_per_delivery_id = fields.Many2one('hr.payment.per.delivery', string='Payment Per Delivery')
    amount = fields.Float(string='Amount')
    quantity = fields.Float(string='Quantity')
    amount_total = fields.Float(string='Amount Total', compute='_compute_amount_total', store=True)

    @api.depends('amount', 'quantity')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.amount * rec.quantity