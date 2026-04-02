from odoo import models, fields, api, _
from itertools import groupby

class UangJalan(models.Model):
    _inherit = 'uang.jalan'

    potongan_claim = fields.Float(string='Potongan Claim',copy=False)
    uang_jalan_driver_claim_id = fields.Many2one('uang.jalan.driver.claim', string='Uang Jalan Driver Claim', copy=False)   
    



    @api.depends('potongan_claim')
    def _compute_total_amount(self):
        super(UangJalan, self)._compute_total_amount()
        for rec in self.filtered(lambda x: x.uang_jalan_driver_claim_id):
            rec.total_amount -= rec.potongan_claim

    def write(self, vals):
        res = super(UangJalan, self).write(vals)
        if 'state' in vals:
            if vals['state'] in ['confirm', 'process', 'done']:
                self._search_uang_jalan_driver_claim()
            elif vals['state'] in ['draft', 'cancel', 'failed']:
                self._remove_uang_jalan_driver_claim()

        return res

    

    def _search_uang_jalan_driver_claim(self):
        uang_jalan_claim_ids = self.env['uang.jalan.driver.claim'].search([('state', '=', 'confirm'), ('driver_id', 'in', self.driver_employee_id.ids)], order='date, id')
        if not uang_jalan_claim_ids:
            return
        for driver_id, group in groupby(self, key=lambda x: x.driver_employee_id):
            uang_jalan_claim = uang_jalan_claim_ids.filtered(lambda x: x.driver_id == driver_id)
            if not uang_jalan_claim:
                continue
            for rec in group:
                if not uang_jalan_claim:
                    break
                current_claim = uang_jalan_claim[0]
                rec.uang_jalan_driver_claim_id = current_claim.id
                potongan_claim = current_claim.persentase_potongan * rec.total_amount / 100
                potongan_claim = min(potongan_claim, current_claim.sisa_potongan)
                rec.potongan_claim = potongan_claim
                if current_claim.sisa_potongan == 0:
                    current_claim.sudo().action_done()
                    uang_jalan_claim -= current_claim
            
    def _remove_uang_jalan_driver_claim(self):
        for rec in self:
            if rec.uang_jalan_driver_claim_id:
                rec.potongan_claim = 0
                if rec.uang_jalan_driver_claim_id.state == 'done':
                    rec.uang_jalan_driver_claim_id.sudo().write({
                        'state': 'confirm',
                    })
                rec.uang_jalan_driver_claim_id = False
                
            
            
                


