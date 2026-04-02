from odoo import models, fields, api, _

class AccountAssetCreateJournalEntry(models.TransientModel):
    _name = 'account.asset.create.journal.entry'
    _description = 'Create Journal Entry for Asset'

    asset_ids = fields.Many2many('account.asset', string='Assets')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    account_id = fields.Many2one('account.account', string='Counterpart Account', required=True, compute='_compute_account_id', store=True, readonly=False)
    partner_id = fields.Many2one('res.partner', string='Customer / Vendor')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    label = fields.Char(string='Label', required=True, default='Journal Entry for Asset')


    @api.depends('journal_id')
    def _compute_account_id(self):
        for record in self:
            if record.journal_id:
                record.account_id = record.journal_id.default_account_id
            else:
                record.account_id = False


    def action_create_journal_entry(self):
        total_value = 0
        move_lines = []
        for asset in self.asset_ids:
            move_lines.append((0, 0, {
                'name': asset.name,
                'debit': asset.value_residual,
                'credit': 0.0,
                'account_id': asset.account_asset_id.id,
                'partner_id': self.partner_id.id,
                'asset_ids' : [(4, asset.id)],
            }))
            total_value += asset.value_residual

        if total_value > 0:
            move_lines.append((0, 0, {
                'name': self.label,
                'debit': 0.0,
                'credit': total_value,
                'account_id': self.account_id.id,
                'partner_id': self.partner_id.id,
            }))

            move = self.env['account.move'].create({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'ref': self.label,
                'line_ids': move_lines,
            })
            move.action_post()

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': move.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window_close',
        }
            
            
        

        