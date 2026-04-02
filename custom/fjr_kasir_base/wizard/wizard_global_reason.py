from odoo import models, fields, api, _
from ast import literal_eval
from odoo.exceptions import UserError

class WizardGlobalReason(models.TransientModel):
    _name = 'wizard.global.reason'
    _description = 'Wizard Global Reason'

    reason = fields.Text(string='Reason', required=True)
    model = fields.Char(string='Model', required=True)
    res_id = fields.Char(string='Resource IDs', required=True)
    action_name = fields.Char('Action Name')



    def action_confirm(self):
        res_ids = literal_eval(self.res_id)
        record = self.env[self.model].browse(res_ids)
        if hasattr(record, self.action_name):
            action_method = getattr(record.with_context(global_reason=self.reason), self.action_name)
            if callable(action_method):
                action_method()
            else:
                raise UserError(_('The action "%s" is not callable on model "%s".') % (self.action_name, self.model))
        else:
            raise UserError(_('The action "%s" does not exist on model "%s".') % (self.action_name, self.model))

   