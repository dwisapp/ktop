from odoo import models, fields, api, _
import uuid
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import random
import string
import requests
import base64
import json
import re
from itertools import groupby
import logging
_logger = logging.getLogger(__name__)

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    

    state = fields.Selection(selection=[
            ('draft', 'To Submit'),
            ('submit', 'Submitted'),
            ('approve', 'Approved By Manager'),
            ('approved_accounting', 'Approved By Accounting'),
            ('approved_accounting_manager', 'Approved By Accounting Manager'),
            ('in_payment', 'In Payment'),
            ('done', 'Done'),
             ('post', 'Posted'),
             ('cancel', 'Refused')
        ])
    midtrans_status = fields.Selection([
        ('queued', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Settlement'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),

    ], string='Midtrans Status', track_visibility='onchange')
    midtrans_reference_no = fields.Char('Midtrans Reference No', copy=False)

    approval_state = fields.Selection(selection_add=[('approved_accounting', 'Approved By Accounting'), ('approved_accounting_manager', 'Approved By Accounting Manager')])
    public_token = fields.Char('Public Token', copy=False)
    approval_link = fields.Char('Approval Link', copy=False)
    rejection_link = fields.Char('Rejection Link', copy=False)
    accounting_id = fields.Many2one('res.users', 'Accounting', copy=False, domain=lambda self: [('groups_id', 'in', self.env.ref('fjr_kasir_expense.group_hr_expense_accounting_user').id)])
    accounting_manager_id = fields.Many2one('res.users', 'Accounting Manager', copy=False, domain=lambda self: [('groups_id', 'in', self.env.ref('fjr_kasir_expense.group_hr_expense_accounting_manager').id)])
    description = fields.Text("Summary")
    name = fields.Char(copy=False,  default=lambda self: _("New"))


    @api.model
    def create(self, vals):
        if vals.get('name', _("New")) == _("New"):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.expense.sheet') or '/'
        return super(HrExpenseSheet, self).create(vals)
    


    def _do_submit(self):
        super(HrExpenseSheet, self)._do_submit()
        for sheet in self:
            if not sheet.user_id:
                raise UserError("Please Input Manager")
            self._generate_public_link('manager')
            sheet.send_whatsapp_approval('manager')

    def _do_approve(self):
        super(HrExpenseSheet, self)._do_approve()
        for sheet in self:
            if not sheet.user_id:
                raise UserError("Please Input Manager")
            sheet.write({'public_token': False, 'approval_link': False, 'rejection_link': False})

    def _do_refuse(self, reason):
        super(HrExpenseSheet, self)._do_refuse(reason)
        for sheet in self:
            sheet.write({'public_token': False, 'approval_link': False, 'rejection_link': False})
        

    def _generate_public_link(self, user_type):
        for sheet in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            public_token = uuid.uuid4().hex
            user_id = sheet.user_id.id
            if user_type == 'accounting':
                user_id = sheet.accounting_id.id
            elif user_type == 'accounting_manager':
                user_id = sheet.accounting_manager_id.id

            approval_url = f'expense/{user_type}/{user_id}/approve/{public_token}'
            rejection_url = f'expense/{user_type}/{user_id}/refuse/{public_token}'
            sheet.write({'public_token': public_token, 'approval_link': approval_url, 'rejection_link': rejection_url})


    def action_approved_accounting_manager(self):
        for sheet in self:
            status_to_update = 'approved_accounting'
            if self.env.user.has_group('fjr_kasir_expense.group_hr_expense_accounting_manager'):
                status_to_update = 'approved_accounting_manager'
            if status_to_update == 'approved_accounting' and sheet.accounting_manager_id:
                sheet._generate_public_link('accounting_manager')
                sheet.request_approval_accounting_manager()
            sheet.write({'approval_state': status_to_update})

    def request_approval_accounting(self):
        for sheet in self:
            if not sheet.accounting_id:
                raise UserError("Please Input Accounting")
            msg = _('Expense Sheet %s requested for approval by %s') % (sheet.name, sheet.accounting_id.name)
            sheet.message_post(body=msg)
            if not sheet.approval_link:
                sheet._generate_public_link('accounting')
            sheet.send_whatsapp_approval('accounting')
            
    
    def request_approval_accounting_manager(self):
        for sheet in self:
            if not sheet.accounting_manager_id:
                raise UserError("Please Input Accounting Manager")
            
            msg = _('Expense Sheet %s requested for approval by %s') % (sheet.name, sheet.accounting_manager_id.name)
            sheet.message_post(body=msg)
            if not sheet.approval_link:
                sheet._generate_public_link('accounting_manager')
            sheet.send_whatsapp_approval('accounting_manager')
    


    def send_whatsapp_approval(self, user_type):
        default_phone = self.user_id.mobile
        default_wa_template_id = self.company_id.expense_whatsapp_approval_template
        if user_type == 'accounting':
            default_phone = self.accounting_id.mobile
        elif user_type == 'accounting_manager':
            default_phone = self.accounting_manager_id.mobile
        elif user_type == 'send_money':
            default_phone = self.env.user.partner_id.mobile
            default_wa_template_id = self.company_id.expense_whatsapp_send_money_template




        context = self._context
        new_context = dict(context)
        new_context.update({
            'active_model' : 'hr.expense.sheet',
            'active_id' : self.id,
            'default_phone' : default_phone,
            'default_wa_template_id': default_wa_template_id,
            'no_partner_notification':True
        })
        whatsapp_composer = self.env['whatsapp.composer'].with_context(new_context).create({
            'phone': default_phone,
            'res_model': 'hr.expense.sheet',
            'res_ids': str(self.id),
        })
        whatsapp_composer._send_whatsapp_template()

    def _check_can_create_move(self):
        if any(sheet.state != 'approved_accounting_manager' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s) by accounting manager."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Specify expense journal to generate accounting entries."))

        missing_email_employees = self.filtered(lambda sheet: not sheet.employee_id.work_email).employee_id
        if missing_email_employees:
            action = self.env['ir.actions.actions']._for_xml_id('hr.open_view_employee_tree')
            action['domain'] = [('id', 'in', missing_email_employees.ids)]
            raise RedirectWarning(_("The work email of some employees is missing. Please add it on the employee form"), action, _("Show missing work email employees"))


    # @api.depends('account_move_ids', 'payment_state', 'approval_state')
    # def _compute_state(self):
    #     super(HrExpenseSheet, self)._compute_state()
    #     for sheet in self:
    #         if sheet.payment_state == 'in_payment':
    #             sheet.state = 'in_payment'

    # @api.depends('midtrans_status', 'account_move_ids.payment_state')
    # def _compute_from_account_move_ids(self):
    #     super(HrExpenseSheet, self)._compute_from_account_move_ids()
    #     for sheet in self.filtered(lambda s: s.payment_mode == 'own_account'):
    #         if not sheet.midtrans_status and sheet.account_move_ids:
    #             sheet.payment_state = 'in_payment'
    #         elif sheet.midtrans_status in ('queued', 'processed'):
    #             sheet.payment_state = 'in_payment'
    #         elif sheet.midtrans_status == 'completed':
    #             sheet.payment_state = 'paid'
    #         elif sheet.midtrans_status == 'failed':
    #             sheet.payment_state = 'failed'

        
        
    def action_transfer_payment(self):
        for sheet in self:
            if not sheet.employee_id.bank_account_id.valid_bank_account:
                sheet.employee_id.bank_account_id.check_valid_for_midtrans()
            if not sheet.employee_id.bank_account_id.valid_bank_account:
                raise UserError(_(f"Bank Account {sheet.employee_id.name} is not valid for Midtrans Payment!"))
        self.create_midtrans_payment()
        public_token = uuid.uuid4().hex
        approval_url = f'expense/payment/{self.env.user.id}/approve/{public_token}'
        rejection_url = f'expense/payment/{self.env.user.id}/refuse/{public_token}'
        self.write({'public_token': public_token, 'approval_link': approval_url, 'rejection_link': rejection_url})
        self.send_whatsapp_approval('send_money')




    def create_midtrans_payment(self):
        if not self.company_id.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not self.company_id.midtrans_payout_iris_api_key:
            raise UserError(_('Please set Midtrans Payout Iris API Key in Company Setting!'))

        url = self.company_id.midtrans_payout_url + '/api/v1/payouts'
        iris_api_key = self.company_id.midtrans_payout_iris_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }

        def create_expense_payment(sheets):
            string_name = " ".join(sheets.mapped('name'))
            cleaned_string_name = re.sub(r'[^a-zA-Z0-9\s]', '', string_name)
            nominal = sum(sheets.mapped('total_amount'))

            data = {
                'payouts' : [
                    {
                        "beneficiary_name": sheets[0].employee_id.bank_account_id.acc_holder_name or sheets[0].employee_id.name,
                        "beneficiary_account": sheets[0].employee_id.bank_account_id.acc_number,
                        "beneficiary_bank": sheets[0].employee_id.bank_account_id.bank_id.midtrans_bank_code,
                        "beneficiary_email": sheets[0].employee_id.work_email or '',
                        "amount": str(nominal),
                        "notes": "Employee Expense %s" % cleaned_string_name,
                    }
                ]
            }

            

            payloads = json.dumps(data)
            response = requests.post(url, headers=headers, data=payloads)
            response_text = response.text
            result = json.loads(response_text)

            payouts = result.get('payouts', [])
            if payouts:
                sheets.write({'midtrans_reference_no': payouts[0].get('reference_no'),
                                        'midtrans_status': payouts[0].get('status')})
                self.env['midtrans.payout.log'].create({
                    'res_id': str(sheets.ids),
                    'reference_no': payouts[0].get('reference_no'),
                    'model_name': 'hr.expense.sheet',
                })

            else:
                raise UserError(_('Failed to create Midtrans Payment!'))
                

        for employee, group in groupby(self, key=lambda x: x.employee_id):
            sheet_ids = self.env['hr.expense.sheet']
            for sheet in group:
                sheet_ids |= sheet
            create_expense_payment(sheet_ids)

        
    def action_approve_payout(self):
        def unique(list1):

            unique_list = []

            for x in list1:
                if x not in unique_list:
                    unique_list.append(x)
            return unique_list
        

        if not self.company_id.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not self.company_id.midtrans_payout_approval_api_key:
            raise UserError(_('Please set Midtrans Payout Iris Approval API Key in Company Setting!'))

        url = self.company_id.midtrans_payout_url + '/api/v1/payouts/approve'
        iris_api_key = self.company_id.midtrans_payout_approval_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }

        data = {
                "reference_nos": unique(self.mapped('midtrans_reference_no')),
                }
        
        payloads = json.dumps(data)
        response = requests.post(url, headers=headers, data=payloads)
        response_text = response.text
        result = json.loads(response_text)
        if not result.get('status', False) == 'ok':
            raise UserError(_('Failed to approve Midtrans Payment!'))
        self.write({'public_token': False, 'approval_link': False, 'rejection_link': False})