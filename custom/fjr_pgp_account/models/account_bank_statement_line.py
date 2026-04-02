from odoo import models, fields, api, _

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    account_id = fields.Many2one(
        comodel_name='account.account',
        check_company=True,
        domain=[['deprecated', '=', False], ['account_type', 'not in', ('asset_cash', 'off_balance')]],
    )



    # @api.model
    # def create(self,vals):
    #     res = super(AccountBankStatementLine,self).create(vals)
    #     if res.account_id:
    #         wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=res.id).new({})
    #         wizard.line_ids[-1].account_id = res.account_id
    #     return res
    

    
    
class BankRecWidgetLine(models.Model):
    _inherit = 'bank.rec.widget'


    def _lines_prepare_auto_balance_line(self):
        res = super(BankRecWidgetLine,self)._lines_prepare_auto_balance_line()
        if self.st_line_id.account_id:
            res['account_id'] = self.st_line_id.account_id.id
        return res

  