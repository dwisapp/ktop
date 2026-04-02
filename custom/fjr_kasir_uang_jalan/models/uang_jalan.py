from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid


class UangJalan(models.Model):
    _name = 'uang.jalan'
    _description = 'Transfer Uang Jalan'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='No. Dokumen', required=True, copy=False,  index=True, default=lambda self: _('New'))
    date = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today)
    rute_uang_jalan_id = fields.Many2one('rute.uang.jalan', string='Uang Jalan')
    tempat_muat = fields.Char(string='Tempat Muat', compute='_compute_uang_jalan_detail', store=True)
    tujuan_bongkar = fields.Char(string='Tujuan Bongkar', compute='_compute_uang_jalan_detail', store=True)
    amount = fields.Float(string='Nominal Uang Jalan', compute='_compute_uang_jalan_detail', store=True)
    adjusted_amount = fields.Float(string='Adjusted Amount', compute='_compute_adjusted_amount')
    driver_employee_id = fields.Many2one('hr.employee', string='Driver', domain=[('is_driver', '=', True)], compute='_compute_from_delivery_notes', store=True, readonly=False)
    driver_partner_id = fields.Many2one('res.partner', string='Driver Partner', related='driver_employee_id.work_contact_id')
    # no_rekening = fields.Char(string='No. Rekening', tracking=True)
    # bank_account_name = fields.Char(string='Bank Account Name')
    # sales_order_id = fields.Many2one('jasa.erp.sales.order', string='Jasa ERP Sales Order')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='restrict', compute='_compute_sale_order_id', store=True, readonly=False, domain="[('id', 'in', available_sale_order_ids)]")
    available_sale_order_ids = fields.Many2many('sale.order', string='Available Sale Orders', compute='_compute_available_sale_order_id')
    delivery_notes_id = fields.Many2one('delivery.note', string='Delivery Note', ondelete='restrict')
    fleet_id = fields.Many2one('fleet.vehicle', string='Kendaraan',tracking=True, compute='_compute_from_delivery_notes', store=True, readonly=False)
    kapal_id = fields.Many2one('kapal.kapal', string='Kapal',tracking=True)
    tipe_uang_jalan_id = fields.Many2one('tipe.uang.jalan', string='Tipe Uang Jalan',tracking=True)
    uang_jalan_category_id = fields.Many2one('uang.jalan.category', string='Kategori Uang Jalan',tracking=True)
    uang_jalan_jenis_barang_id = fields.Many2one('uang.jalan.jenis.barang', string='Jenis Barang', tracking=True)
    tanggal_transfer = fields.Datetime(string='Tanggal Transfer', tracking=True)
    notes = fields.Html(string='Catatan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True, copy=False)
    uang_jalan_adjust_line_ids = fields.One2many('uang.jalan.adjust.line', 'uang_jalan_id', string='Adjustment Line')
    midtrans_status = fields.Selection([
        ('queued', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Settlement'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),

    ], string='Midtrans Status', tracking=True)
    xendit_status = fields.Selection([
        ('ACCEPTED', 'Accepted'),
        ('CANCELLED', 'Cancelled'),
        ('SUCCEEDED', 'Succeeded'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
    ], string='Xendit Status', tracking=True)

    midtrans_reference_no = fields.Char(string='Midtrans Reference No', tracking=True)
    xendit_reference_no = fields.Char(string='Xendit Reference No', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account', domain="[('partner_id', '=', driver_partner_id)]",
                                       tracking=True, compute='_compute_bank_account_id', store=True, readonly=False)
    # bank_id = fields.Many2one('res.bank', string='Bank', domain="[('midtrans_bank_code', '!=', False)]")
    valid_bank_account = fields.Boolean(string='Valid Bank Account', help='Check if the bank account is valid for Midtrans Payout', related="bank_account_id.valid_bank_account")
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    # jasa_erp_delivery_note_id = fields.Many2one('jasa.erp.delivery.note', string='Jasa ERP Delivery Note')


    @api.depends('bank_account_id')
    def _compute_valid_bank_account(self):
        for rec in self:
            rec.valid_bank_account = bool(rec.bank_account_id and rec.bank_account_id.acc_number)

    @api.depends('driver_partner_id')
    def _compute_bank_account_id(self):
        for rec in self:
            rec.bank_account_id = rec.driver_partner_id.bank_ids and rec.driver_partner_id.bank_ids[0]



    @api.depends('delivery_notes_id')
    def _compute_sale_order_id(self):
        for rec in self:
            rec.sale_order_id = rec.delivery_notes_id.sale_order_ids[0] if rec.delivery_notes_id.sale_order_ids else False


    @api.depends('delivery_notes_id')
    def _compute_from_delivery_notes(self):
        for rec in self:
            rec.driver_employee_id = rec.delivery_notes_id.driver_employee_id
            rec.fleet_id = rec.delivery_notes_id.fleet_id
            

    @api.depends('delivery_notes_id')
    def _compute_available_sale_order_id(self):
        for rec in self:
            rec.available_sale_order_ids = rec.delivery_notes_id.sale_order_ids.filtered(lambda x: x.state == 'sale')

    @api.depends('amount', 'adjusted_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount + rec.adjusted_amount

    def random_midtrans_status(self):
        # reference_no = str(uuid.uuid4())[0:10]

        # self.env['midtrans.payout.log'].create({
        #             'res_id': str(self.ids),
        #             'reference_no': reference_no,
        #             'model_name': 'uang.jalan',
        #         })
        
        # self.write({'midtrans_reference_no': reference_no})
        self.write({
            'midtrans_status' : 'completed'
        })

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('Hanya Uang Jalan Draft yang bisa di hapus')
        return super(UangJalan, self).unlink()

    def write(self,vals):
        if vals.get('bank_account_id'):
            vals['midtrans_status'] = False
            vals['midtrans_reference_no'] = False
            vals['xendit_status'] = False
            vals['xendit_reference_no'] = False

        if 'midtrans_status' in vals:
            midtrans_status = vals.get('midtrans_status')
            if midtrans_status == 'completed':
                vals.update({'state': 'done'})
                
            elif midtrans_status == 'failed':
                vals.update({'state': 'failed'})
            elif midtrans_status == 'processed':
                vals.update({'state': 'process'})

        if 'xendit_status' in vals:
            xendit_status = vals.get('xendit_status')
            if xendit_status == 'SUCCEEDED':
                vals.update({'state': 'done'})
            elif xendit_status == 'FAILED' or xendit_status == 'CANCELLED':
                vals.update({'state': 'failed'})
            elif xendit_status == 'ACCEPTED':
                vals.update({'state': 'process'})

        if vals.get('state') == 'done':
            for rec in self:
                rec._trigger_action_after_done()
        return super(UangJalan, self).write(vals)


    def _trigger_action_after_done(self):
        """Trigger action after Uang Jalan is done"""

    def action_adjust_uang_jalan(self):
        return {
            'name': _('Adjust Uang Jalan'),
            'type': 'ir.actions.act_window',
            'res_model': 'uang.jalan.adjust.line',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_uang_jalan_id': self.id,
            }
        }

    def action_confirm(self):
        self = self.filtered(lambda x : x.state =='draft')
        if not self:
            raise UserError("Hanya Uang Jalan Draft yang dapat di confirm")

        self.write({'state': 'confirm'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_send(self):
        self = self.filtered(lambda x : x.state =='confirm')
        if not self:
            raise UserError('Hanya Uang Jalan yang sudah Confirm yang bisa di kirim')
        # if len(self.driver_partner_id.ids) != 1:
        #     raise UserError("Hanya bisa mengirimkan Uang Jalan untuk 1 Driver")
        
        amount = sum(self.mapped('total_amount'))
            


        return {
            'name': _('Anda Akan Mengirimkan Uang Jalan Sebesar %s' % ((amount))),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.verifikasi.bca',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_uang_jalan_ids': self.ids,
                'default_nominal_uang_jalan': ((amount)),
            }
        }
    

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('uang.jalan') or _('New')
        return super(UangJalan, self).create(vals)
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.env['ir.sequence'].next_by_code('uang.jalan') or _('New')
        return super(UangJalan, self).copy(default)


    def send_whatsapp(self):
        context = self._context
        new_context = dict(context)
        new_context.update({
            'active_model' : 'uang.jalan',
            'active_ids' : self.ids,
            # 'default_phone' : self.driver_partner_id.mobile,
        })
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'whatsapp.composer',
                'view_mode': 'form',
                'target': 'new',
                'context': new_context
            }

    @api.depends('rute_uang_jalan_id')
    def _compute_uang_jalan_detail(self):
        for rec in self:
            rec.tempat_muat = rec.rute_uang_jalan_id.tempat_muat
            rec.tujuan_bongkar = rec.rute_uang_jalan_id.tujuan_bongkar
            rec.amount = rec.rute_uang_jalan_id.amount

    @api.depends('uang_jalan_adjust_line_ids.amount')
    def _compute_adjusted_amount(self):
        for rec in self:
            adjusted_amount = sum(rec.uang_jalan_adjust_line_ids.mapped('amount'))
            rec.adjusted_amount = adjusted_amount


class UangJalanAdjustLine(models.Model):
    _name = 'uang.jalan.adjust.line'


    uang_jalan_id = fields.Many2one('uang.jalan', string='Uang Jalan')
    name = fields.Text(string='Keterangan', required=True)
    amount = fields.Float(string='Amount')

    @api.model
    def create(self,vals):
        uang_jalan_id = self.env['uang.jalan'].browse(vals.get('uang_jalan_id'))
        if uang_jalan_id.adjusted_amount + vals.get('amount') + uang_jalan_id.amount < 0:
            raise UserError('Total Adjusted Amount tidak boleh kurang dari 0')
        if uang_jalan_id.midtrans_status:
            uang_jalan_id.write({'midtrans_status': False, 'midtrans_reference_no': False})

        return super(UangJalanAdjustLine, self).create(vals)