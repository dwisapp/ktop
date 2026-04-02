from odoo import models, fields, api, _

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    use_delivery_note = fields.Boolean(string='Use Delivery Note', default=False)