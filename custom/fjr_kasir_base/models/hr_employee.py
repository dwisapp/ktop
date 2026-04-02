from odoo import models, fields, api, _

class HrEmployee(models.AbstractModel):
    _inherit = 'hr.employee.base'

    is_driver = fields.Boolean(string="Driver?")
