from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    
    sequence_year_range_regex = fields.Text(string='Sequence Year Range Regex', help="This field is used to define the year range for the sequence. The format is 'YYYY-YYYY'. Example: '2021-2022'")
    sequence_yearly_regex = fields.Text(string='Sequence Yearly Regex')
    sequence_monthly_regex = fields.Text(string='Sequence Monthly Regex')
    invoice_sequence_id = fields.Many2one('ir.sequence', string='Invoice Sequence', help="This field is used to define the invoice sequence for this journal. If not set, the system will use the default invoice sequence.")


    def create_internal_transfer(self):
        """return action to create a internal transfer"""
        return self.open_payments_action('transfer', mode='form')
    
    
    