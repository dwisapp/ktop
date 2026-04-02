from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrPerhitunganPPh(models.Model):
    _name = 'hr.perhitungan.pph'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    hr_kategori_ter_id = fields.Many2one('hr.kategori.ter', string='Kategori TER PPh')
    amount_min = fields.Float(string='Amount Min')
    amount_max = fields.Float(string='Amount Max')
    tarif = fields.Float(string='Tarif (%)')

    @api.depends('hr_kategori_ter_id','amount_min', 'amount_max')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.hr_kategori_ter_id.name + " - " + str(rec.amount_min) + ' - ' + str(rec.amount_max) if rec.amount_max else ''

    @api.constrains('hr_kategori_ter_id','amount_min', 'amount_max')
    def _check_amount_min_max(self):
        for rec in self:
            if rec.amount_min and rec.amount_max:
                if rec.amount_min >= rec.amount_max:
                    raise UserError(_('Amount Min should be less than Amount Max!'))
                # (hrl.checkin <= %s AND hrl.checkout >= %s) OR (hrl.checkin <= %s AND hrl.checkout >= %s)
                # self.env.cr.execute('''
                #     SELECT name FROM lapisan_uu_hpp WHERE (amount_min <= %s AND amount_max >= %s) OR (amount_min <= %s AND amount_max >= %s) AND id != %s
                # ''', (rec.amount_min, rec.amount_min, rec.amount_max, rec.amount_max, rec.id))
                # duplicate = self.env.cr.fetchone()

                # duplicate = self.search(['|','|','&',('amount_min', '<=', rec.amount_min),
                #  ('amount_max', '>=', rec.amount_min),'&',('amount_min', '<=', rec.amount_max),
                # ('amount_max', '>=', rec.amount_max),'&',('amount_min', '>=', rec.amount_min), 
                # ('amount_max', '<=', rec.amount_max),
                # ('id','!=',rec.id)], limit=1)
                duplicate = self.search([

                ('id', '!=', rec.id),
                ('hr_kategori_ter_id', '=', rec.hr_kategori_ter_id.id),
                '|', '|',
                '&', ('amount_min', '<=', rec.amount_min), ('amount_max', '>=', rec.amount_min),
                '&', ('amount_min', '<=', rec.amount_max), ('amount_max', '>=', rec.amount_max),
                '&', ('amount_min', '>=', rec.amount_min), ('amount_max', '<=', rec.amount_max)
            ], limit=1)
                if duplicate:
                    raise UserError(_('Amount Min and Amount Max already exist in ' + duplicate.name))