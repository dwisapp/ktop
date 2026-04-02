from odoo import models, fields, api, _

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    
    

    def _get_line_batch_key(self, line):
        result = super(AccountPaymentRegister, self)._get_line_batch_key(line)
        result['partner_bank_id'] = False
        return result