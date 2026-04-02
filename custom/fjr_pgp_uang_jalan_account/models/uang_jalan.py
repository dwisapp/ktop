from odoo import models, fields, api, _
from odoo.exceptions import UserError

class UangJalan(models.Model):
    _inherit = 'uang.jalan'


    move_id = fields.Many2one('account.move', string='Journal Entries', copy=False)
    statement_line_id = fields.Many2one('account.bank.statement.line', string='Bank Statement Line', copy=False)

    def write(self, vals):
        res = super(UangJalan, self).write(vals)
        if 'sale_order_id' in vals:
            for rec in self.filtered(lambda x: x.state == 'done'):
                rec._create_move()
        return res

    def action_manual_send(self):
        self.write({'state': 'done', 'midtrans_status' : 'completed'})

 
    def action_send(self):
        if not self.company_id.account_uang_jalan_id:
            raise UserError(_('Please configure the Account Uang Jalan in the company settings.'))
        
        if not self.company_id.journal_uang_jalan_id:
            raise UserError(_('Please configure the Journal Uang Jalan in the company settings.'))
        
        return super(UangJalan, self).action_send()
    
    def action_cancel(self):
        res = super(UangJalan, self).action_cancel()
        if self.move_id:
            self.move_id.with_user(self.env.user).sudo().button_cancel()
            # self.move_id.unlink()
        return res
    

    def _trigger_action_after_done(self):
        res = super(UangJalan, self)._trigger_action_after_done()
        self._create_move()
        return res
    
    

    def _create_move(self):
        self = self.with_user(self.env.user).sudo()
        journal_id = self.company_id.journal_uang_jalan_id
        statement_line_id = self.statement_line_id
        account_id = self.company_id.account_uang_jalan_id.id
        analytic_account_id = self.sale_order_id.analytic_account_id
        analytic_distribution = {}
        if analytic_account_id:
            analytic_distribution = {
                analytic_account_id.id: 100
            }

        if statement_line_id:
            if statement_line_id.is_reconciled:
                wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=statement_line_id.id).new({})
                wizard._js_action_reset()


            statement_line_id.write({
                'payment_ref': self.name,
                'partner_id': self.driver_employee_id.work_contact_id.id,
                'amount': -self.total_amount,
                'date': self.date,
            })

        else:
            statement_line_id = self.env['account.bank.statement.line'].create({
                'payment_ref': self.name,
                'partner_id': self.driver_employee_id.work_contact_id.id,
                'amount': -self.total_amount,
                'date': self.date,
                'journal_id': journal_id.id,
            })


        wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=statement_line_id.id).new({})
        wizard.line_ids[-1].write({
            'account_id': account_id,
            'analytic_distribution' : analytic_distribution,
        })
        wizard._js_action_validate()
        self.write({'statement_line_id': statement_line_id.id, 'move_id': statement_line_id.move_id.id})

    def action_open_journal_entries(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        action['res_id'] = self.move_id.id
        action['views'] = [(False, 'form')]
        return action
    

    
            
            

