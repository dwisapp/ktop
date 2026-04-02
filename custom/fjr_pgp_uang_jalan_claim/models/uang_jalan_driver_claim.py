from odoo import models, fields, api, _
from odoo.exceptions import UserError

class UangJalanDriverClaim(models.Model):
    _name = 'uang.jalan.driver.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Uang Jalan Driver Claim'

    name = fields.Char(string='Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    driver_id = fields.Many2one('hr.employee', string='Driver', required=True, domain=[('is_driver', '=', True)], tracking=True)
    keterangan = fields.Text(string='Keterangan',tracking=True)
    uang_jalan_ids = fields.One2many('uang.jalan', 'uang_jalan_driver_claim_id', string='Uang Jalan',domain=[('state', 'in', ['confirm', 'process', 'done'])])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', readonly=True, copy=False, tracking=True)
    amount = fields.Float(string='Amount', tracking=True)
    total_potongan = fields.Float(string='Total Potongan', compute='_compute_total_potongan', store=True)
    persentase_potongan = fields.Float(string='Potongan (%)', default=1)
    sisa_potongan = fields.Float(string='Sisa Potongan', compute='_compute_sisa_potongan', store=True)


    @api.depends('uang_jalan_ids.potongan_claim')
    def _compute_total_potongan(self):
        for rec in self:
            rec.total_potongan = sum(rec.uang_jalan_ids.mapped('potongan_claim'))

    @api.depends('total_potongan', 'amount')
    def _compute_sisa_potongan(self):
        for rec in self:
            rec.sisa_potongan = rec.amount - rec.total_potongan

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('uang.jalan.driver.claim') or _('New')
        return super(UangJalanDriverClaim, self).create(vals)
    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can only delete draft records!'))
        return super(UangJalanDriverClaim, self).unlink()


    def action_confirm(self):
        draft_state = self.filtered(lambda x: x.state == 'draft')
        if not draft_state:
            raise UserError(_('Only draft state can be confirmed!'))
        
        if draft_state.filtered(lambda x: x.amount <= 0):
            raise UserError(_('Amount must be greater than 0!'))
        draft_state.write({'state': 'confirm'})


    def action_cancel(self):
        self_with_uang_jalan = self.filtered(lambda x: x.uang_jalan_ids)
        if self_with_uang_jalan:
            raise UserError(_('Only Claim without Uang Jalan can be cancelled!'))
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_done(self):
        self.write({'state': 'done'})
    