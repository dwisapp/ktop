from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    use_midtrans_payout = fields.Boolean(string='Use Midtrans Payout', help='Enable to use Midtrans Payout', related='company_id.use_midtrans_payout', readonly=False)
    midtrans_payout_url = fields.Char(string='Midtrans Payout URL', help='URL for Midtrans Payout', related='company_id.midtrans_payout_url', readonly=False)
    midtrans_payout_iris_api_key = fields.Char(string='Midtrans Payout Iris API Key', help='Iris API Key for Midtrans Payout', related='company_id.midtrans_payout_iris_api_key', readonly=False)
    midtrans_payout_approval_api_key = fields.Char(string='Midtrans Payout Approval API Key', help='Approval API Key for Midtrans Payout', related='company_id.midtrans_payout_approval_api_key', readonly=False)
  


    use_xendit_payout = fields.Boolean(string='Use Xendit Payout', help='Enable to use Xendit Payout', related='company_id.use_xendit_payout', readonly=False)
    xendit_payout_url = fields.Char(string='Xendit Payout URL', help='URL for Xendit Payout', related='company_id.xendit_payout_url', readonly=False)
    xendit_payout_api_key = fields.Char(string='Xendit Payout API Key', help='API Key for Xendit Payout', related='company_id.xendit_payout_api_key', readonly=False)
    xendit_payout_webhook_token = fields.Char(string='Xendit Payout Webhook Token', help='Webhook Token for Xendit Payout', config_parameter='xendit.payout.webhook.token')

    @api.onchange('use_midtrans_payout', 'use_xendit_payout')
    def _onchange_use_payout_methods(self):
        if self.use_midtrans_payout and self.use_xendit_payout:
            raise UserError(_('You can only enable one payout method at a time. Please disable one before enabling the other.'))


    def create_list_of_bank_from_api(self):
        self.env['res.bank'].create_list_of_bank_from_api()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }