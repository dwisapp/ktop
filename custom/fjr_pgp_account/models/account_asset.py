from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'


    def action_create_journal_entry(self):
        self_with_fixed_account = self.filtered(lambda x: x.account_asset_id and x.state != 'cancel')
        if not self_with_fixed_account:
            raise UserError(_('You cannot create a journal entry for assets without a fixed asset account.'))
        return {
            'name': _('Create Journal Entry'),
            'view_mode': 'form',
            'res_model': 'account.asset.create.journal.entry',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_asset_ids': [(6, 0, self.ids)],
            },
        }