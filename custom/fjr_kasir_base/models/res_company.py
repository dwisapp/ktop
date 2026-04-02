from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
class ResCompany(models.Model):
    _inherit = 'res.company'

    use_midtrans_payout = fields.Boolean(string='Use Midtrans Payout', default=False, help='Enable to use Midtrans Payout')
    midtrans_payout_url = fields.Char(string='Midtrans Payout URL', help='URL for Midtrans Payout')
    midtrans_payout_iris_api_key = fields.Char(string='Midtrans Payout Iris API Key', help='Iris API Key for Midtrans Payout')
    midtrans_payout_approval_api_key = fields.Char(string='Midtrans Payout Approval API Key', help='Approval API Key for Midtrans Payout')


    use_xendit_payout = fields.Boolean(string='Use Xendit Payout', default=False, help='Enable to use Xendit Payout')
    xendit_payout_url = fields.Char(string='Xendit Payout URL', help='URL for Xendit Payout')
    xendit_payout_api_key = fields.Char(string='Xendit Payout API Key', help='API Key for Xendit Payout')



    draft_watermark = fields.Binary("Draft Watermark")
    approved_watermark = fields.Binary("Approved Watermark")



    @api.constrains('use_midtrans_payout', 'use_xendit_payout')
    def _check_payout_methods(self):
        for company in self:
            if company.use_midtrans_payout and company.use_xendit_payout:
                raise ValidationError(_('You can only enable one payout method at a time. Please disable one before enabling the other.'))