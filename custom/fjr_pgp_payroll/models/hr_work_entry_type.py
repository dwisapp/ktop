from odoo import models, fields, api, _

class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'


    display_in_payslip = fields.Boolean(string='Display in Payslip', default=False)

