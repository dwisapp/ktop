from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import base64
import json


class ResBank(models.Model):
    _inherit = 'res.bank'

    midtrans_bank_code = fields.Char(string='Midtrans Bank Code', help='Bank Code for Midtrans Payout')
    xendit_bank_code = fields.Char(string='Xendit Bank Code', help='Bank Code for Xendit Payout')

    @api.model
    def create_list_of_bank_from_api(self):
        if not self.env.company.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not self.env.company.midtrans_payout_iris_api_key:
            raise UserError(_('Please set Midtrans Payout Iris API Key in Company Setting!'))
        
        url = self.env.company.midtrans_payout_url + '/api/v1/beneficiary_banks'

        iris_api_key = self.env.company.midtrans_payout_iris_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }

        response = requests.get(url, headers=headers)
        data = response.text
        data = json.loads(data)
        

        saved_data = self.search([]).mapped('midtrans_bank_code')

        for bank in data.get('beneficiary_banks', []):
            if bank.get('code') not in saved_data:
                self.create({
                    'name': bank.get('name'),
                    'midtrans_bank_code': bank.get('code'),
                })

    def check_valid_for_midtrans(self, account_no):
        if not self.env.company.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not self.env.company.midtrans_payout_iris_api_key:
            raise UserError(_('Please set Midtrans Payout Iris API Key in Company Setting!'))


        url = f'{self.env.company.midtrans_payout_url}/api/v1/account_validation?bank={self.midtrans_bank_code}&account={account_no}'
        iris_api_key = self.env.company.midtrans_payout_iris_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }
    
        response = requests.get(url, headers=headers)
        data = response.text
        data = json.loads(data)
        if data.get('account_no', False) == account_no:
            return True
        return False
    
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    valid_bank_account = fields.Boolean(string='Valid Bank Account', default=False)


    def check_valid_for_midtrans(self):
        account_no = self.acc_number
        if not self.env.company.midtrans_payout_url:
            raise UserError(_('Please set Midtrans Payout URL in Company Setting!'))
        if not self.env.company.midtrans_payout_iris_api_key:
            raise UserError(_('Please set Midtrans Payout Iris API Key in Company Setting!'))


        url = f'{self.env.company.midtrans_payout_url}/api/v1/account_validation?bank={self.bank_id.midtrans_bank_code}&account={account_no}'
        iris_api_key = self.env.company.midtrans_payout_iris_api_key + ':'
        api_key = base64.b64encode(iris_api_key.encode('utf-8')).decode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key,
            'Accept': 'application/json',
        }
    
        response = requests.get(url, headers=headers)
        data = response.text
        data = json.loads(data)
        if data.get('account_no', False) == account_no:
            self.valid_bank_account = True
            return True
        return False

