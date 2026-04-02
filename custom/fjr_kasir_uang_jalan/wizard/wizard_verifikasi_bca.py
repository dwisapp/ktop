from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import string
import requests
import base64
import json
import re
from itertools import groupby
import logging
import uuid

_logger = logging.getLogger(__name__)

class WizardVefifikasiBca(models.Model):
    _name = 'wizard.verifikasi.bca'
    _description = 'Verifikasi Uang Jalan'

    uang_jalan_ids = fields.Many2many('uang.jalan', string='Uang Jalan')
    nominal_uang_jalan = fields.Float(string='Nominal Uang Jalan')
    kode_verifikasi = fields.Char(string='Kode Verifikasi')
    current_kode_verifikasi = fields.Char(string='Current Kode Verifikasi')


    def action_generate_kode_verifikasi(self):
        if not self.current_kode_verifikasi:
            letters = string.ascii_letters
            random_letters = ''.join(random.choice(letters) for i in range(5))
            self.current_kode_verifikasi = random_letters

        

            # if uj.driver_employee_id.bank_pembayaran_id == uj.bank_id and uj.driver_employee_id.no_rekening == uj.no_rekening: 
            #     uj.driver_employee_id.write({'valid_bank_account': True})
        

        uang_jalan_with_midtrans = self.uang_jalan_ids.filtered(lambda x: x.company_id.use_midtrans_payout)
        if uang_jalan_with_midtrans:
            for uj in uang_jalan_with_midtrans:
                if not uj.valid_bank_account:
                    uj.valid_bank_account = uj.bank_account_id.check_valid_for_midtrans()
                
                if not uj.valid_bank_account:
                    raise UserError(_(f'Bank Account {uj.name} is not valid for Midtrans Payout!'))

            self.create_midtrans_payment(uang_jalan_with_midtrans)
        
        


        self.send_whatsapp()
        # self.action_confirm()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.verifikasi.bca',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
        }
    
    def create_midtrans_payment(self, uang_jalan_ids):
        if not uang_jalan_ids.company_id.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not uang_jalan_ids.company_id.midtrans_payout_iris_api_key:
            raise UserError(_('Please set Midtrans Payout Iris API Key in Company Setting!'))

        url = uang_jalan_ids.company_id.midtrans_payout_url + '/api/v1/payouts'
        iris_api_key = uang_jalan_ids.company_id.midtrans_payout_iris_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }

        def create_uang_jalan(uang_jalans):
            string_name = " ".join(uang_jalans.mapped('name'))
            cleaned_string_name = re.sub(r'[^a-zA-Z0-9\s]', '', string_name)
            nominal = sum(uang_jalans.mapped('total_amount'))

            bank_code = uang_jalans[0].bank_account_id.bank_id.midtrans_bank_code
            if not bank_code:
                raise UserError(_(f'Bank {uang_jalans[0].bank_account_id.bank_id.name} does not have Midtrans Bank Code! Please update the bank data from Midtrans API.'))
            data = {
                'payouts' : [
                    {
                        "beneficiary_name": uang_jalans[0].bank_account_id.acc_holder_name or uang_jalans[0].driver_employee_id.name,
                        "beneficiary_account": uang_jalans[0].bank_account_id.acc_number,
                        "beneficiary_bank": uang_jalans[0].bank_account_id.bank_id.midtrans_bank_code,
                        "beneficiary_email": uang_jalans[0].driver_employee_id.work_email or '',
                        "amount": str(nominal),
                        "notes": "Uang Jalan %s" % cleaned_string_name,
                    }
                ]
            }

            

            payloads = json.dumps(data)
            response = requests.post(url, headers=headers, data=payloads)
            response_text = response.text
            result = json.loads(response_text)

            payouts = result.get('payouts', [])
            if payouts:
                uang_jalans.write({'midtrans_reference_no': payouts[0].get('reference_no'),
                                        'midtrans_status': payouts[0].get('status')})
                self.env['midtrans.payout.log'].create({
                    'res_id': str(uang_jalans.ids),
                    'reference_no': payouts[0].get('reference_no'),
                    'model_name': 'uang.jalan',
                })

            else:
                _logger.error('Failed to create Midtrans Payment!', response_text)
                raise UserError(_('Failed to create Midtrans Payment!'))
                

        # uang_jalan_ids = uang_jalan_ids.sorted(key=lambda x:x.driver_employee_id)
        for driver_employee_id, group in groupby(uang_jalan_ids, key=lambda x: x.driver_employee_id):
            current_uang_jalan_ids = self.env['uang.jalan']
            for uj in group:
                current_uang_jalan_ids |= uj
            create_uang_jalan(current_uang_jalan_ids)

        

    def create_xendit_payment(self, uang_jalan_ids):
        if not uang_jalan_ids.company_id.xendit_payout_url:
            raise UserError(_('Please set Xendit Payout URL in Company Setting!'))
        if not uang_jalan_ids.company_id.xendit_payout_api_key:
            raise UserError(_('Please set Xendit Payout API Key in Company Setting!'))

        url = uang_jalan_ids.company_id.xendit_payout_url 
        xendit_api_key = uang_jalan_ids.company_id.xendit_payout_api_key + ':'
        api_key = base64.b64encode(xendit_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
            'Idempotency-Key': str(uuid.uuid4()),
        }

        def create_uang_jalan(uang_jalans):
            string_name = " ".join(uang_jalans.mapped('name'))
            cleaned_string_name = re.sub(r'[^a-zA-Z0-9\s]', '', string_name)
            nominal = sum(uang_jalans.mapped('total_amount'))


            bank_code = uang_jalans[0].bank_account_id.bank_id.xendit_bank_code
            if not bank_code:
                raise UserError(_(f'Bank {uang_jalans[0].bank_account_id.bank_id.name} does not have Xendit Bank Code! Please update the bank data from Xendit API.'))


            data = {
                "reference_id": cleaned_string_name,
                "channel_code": uang_jalans[0].bank_account_id.bank_id.xendit_bank_code,
                "channel_properties": {
                    "account_number": uang_jalans[0].bank_account_id.acc_number,
                    "account_holder_name": uang_jalans[0].bank_account_id.acc_holder_name or uang_jalans[0].driver_employee_id.name,
                },
                "amount": nominal,
                "currency": "IDR",
                "description": cleaned_string_name,
            }

            

            payloads = json.dumps(data)

            print("headers----------------------------", headers)
            response = requests.post(url, headers=headers, data=payloads)
            response_text = response.text
            result = json.loads(response_text)

            xendit_id = result.get('id', False)
            if xendit_id:
                uang_jalans.write({'xendit_reference_no': xendit_id,
                                        'xendit_status': result.get('status')})
                self.env['xendit.payout.log'].create({
                    'res_id': str(uang_jalans.ids),
                    'reference_no': xendit_id,
                    'amount': result.get('amount'),
                    'model_name': 'uang.jalan',
                })

            else:
                _logger.error('Failed to create Xendit Payment!', response_text)
                raise UserError(_('Failed to create Xendit Payment!'))
                

        # uang_jalan_ids = uang_jalan_ids.sorted(key=lambda x:x.driver_employee_id)
        for driver_employee_id, group in groupby(uang_jalan_ids, key=lambda x: x.driver_employee_id):
            current_uang_jalan_ids = self.env['uang.jalan']
            for uj in group:
                current_uang_jalan_ids |= uj
            create_uang_jalan(current_uang_jalan_ids)


    
    def send_whatsapp(self):
        context = self._context
        new_context = dict(context)
        new_context.update({
            'active_model' : 'wizard.verifikasi.bca',
            'active_id' : self.id,
            'default_phone' : self.env.user.partner_id.mobile,
            'no_partner_notification':True
        })
        whatsapp_composer = self.env['whatsapp.composer'].with_context(new_context).create({
            'phone': self.env.user.partner_id.mobile,
            'res_model': 'wizard.verifikasi.bca',
            'res_ids': str(self.id),
        })
        whatsapp_composer._send_whatsapp_template()


    def approve_payout(self):
        uang_jalan_with_midtrans = self.uang_jalan_ids.filtered(lambda x: x.company_id.use_midtrans_payout)
        if uang_jalan_with_midtrans:
            self.approve_payout_midtrans(uang_jalan_with_midtrans)
        
        uang_jalan_with_xendit = self.uang_jalan_ids.filtered(lambda x: x.company_id.use_xendit_payout)
        if uang_jalan_with_xendit:
            self.create_xendit_payment(uang_jalan_with_xendit)



    def approve_payout_midtrans(self,uang_jalan_ids):
        def unique(list1):

            unique_list = []

            for x in list1:
                if x not in unique_list:
                    unique_list.append(x)
            return unique_list


        if not uang_jalan_ids.company_id.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not uang_jalan_ids.company_id.midtrans_payout_approval_api_key:
            raise UserError(_('Please set Midtrans Payout Iris Approval API Key in Company Setting!'))

        url = uang_jalan_ids.company_id.midtrans_payout_url + '/api/v1/payouts/approve'
        iris_api_key = uang_jalan_ids.company_id.midtrans_payout_approval_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }

        data = {
                "reference_nos": unique(uang_jalan_ids.mapped('midtrans_reference_no')),
                }

        payloads = json.dumps(data)
        response = requests.post(url, headers=headers, data=payloads)
        response_text = response.text
        result = json.loads(response_text)
        if not result.get('status', False) == 'ok':
            raise UserError(_('Failed to approve Midtrans Payment!'))
        

    def action_confirm(self):
        # Bypass OTP - langsung approve tanpa cek kode verifikasi
        # if self.kode_verifikasi == self.current_kode_verifikasi:
        self.approve_payout()
        self.uang_jalan_ids.write({'state': 'process', 'tanggal_transfer': fields.Datetime.now()})
        return self.uang_jalan_ids.send_whatsapp()
        # else:
        #     raise UserError(_('Kode Verifikasi Salah!'))