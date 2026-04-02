from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'


    # is_pph21 = fields.Boolean(string='PPh21 ?', default=False)

    # def _compute_rule(self, localdict):
    #     result, qty, rate = super(HrSalaryRule, self)._compute_rule(localdict)
    #     if self.is_pph21:
    #         employee = localdict.get('employee')
    #         if not employee.hr_kategori_pph_id:
    #             # raise UserError(_("Employee %s doesn't have Kategori PPh" % employee.name))
    #             return result, qty, rate
            
    #         pph_tingkatan = self.env['hr.perhitungan.pph'].search([('amount_min','<=',result),('amount_max','>=',result),
    #                                                                ('hr_kategori_ter_id','=',employee.hr_kategori_ter_id.id)], limit=1)
    #         if not pph_tingkatan:
    #             raise UserError(_("PPh21 not found for amount %s" % result))
    #         # result = result * (pph_tingkatan.tarif / 100)
    #         # localdict['result'] = result
    #         rate = pph_tingkatan.tarif
    #         localdict['result_rate'] = pph_tingkatan.tarif


    #     return result, qty, rate