from odoo import models, fields, api, _

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     midtrans_payout_url = fields.Char(string='Midtrans Payout URL', help='URL for Midtrans Payout', related='company_id.midtrans_payout_url', readonly=False)
#     midtrans_payout_iris_api_key = fields.Char(string='Midtrans Payout Iris API Key', help='Iris API Key for Midtrans Payout', related='company_id.midtrans_payout_iris_api_key', readonly=False)
#     midtrans_payout_approval_api_key = fields.Char(string='Midtrans Payout Approval API Key', help='Approval API Key for Midtrans Payout', related='company_id.midtrans_payout_approval_api_key', readonly=False)
  
#     def create_list_of_bank_from_api(self):
#         self.env['res.bank'].create_list_of_bank_from_api()
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'reload',
#         }