from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeliveryNote(models.Model):
    _name = 'delivery.note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Delivery Note'


    name = fields.Char(string='Delivery No.', required=True, copy=False,  index=True, default=lambda self: _('New'), tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence', domain="[('code', '=', 'delivery.note')]", 
                                  default=lambda self: self.env['ir.sequence'].search([('code', '=', 'delivery.note')], limit=1), tracking=True)
    customer_order_ref = fields.Char(string='Customer Order Ref', tracking=True)
    delivery_start_date = fields.Datetime(string='Delivery Start Date', tracking=True)
    delivery_finish_date = fields.Datetime(string='Delivery Finish Date', tracking=True)
    
    transporter_id = fields.Many2one('res.partner', string='Transporter', domain=[('is_transporter', '=', True)], tracking=True)
    driver_id = fields.Many2one('res.partner', string='Driver Partner', domain=[('is_driver', '=', True)], tracking=True)
    driver_employee_id = fields.Many2one('hr.employee', string='Driver', tracking=True, domain=[('is_driver', '=', True)])
    transport_receipt_no = fields.Char(string='Transport Receipt No.')
    fleet_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    distance = fields.Float(string='Distance (km)')
    transport_mode = fields.Selection([
        ('road', _('Road')),
        ('ship', _('Ship')),
        ('air', _('Air')),
        ('rail', _('Rail')),
        ('other', _('Other')),
    ], string='Transport Mode')
    transport_receipt_date = fields.Datetime(string='Transport Receipt Date')

    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    employee_barcode = fields.Char('Employee ID', related='employee_id.barcode', readonly=True)
    unit_type = fields.Char(string='Unit Type')

    jenis_barang = fields.Char(string='Jenis Barang', tracking=True)
    tujuan_bongkar = fields.Char(string='Detail Tujuan Bongkar', tracking=True)
    tempat_muat = fields.Char(string='Detail Tempat Muat', tracking=True)
    tempat_muat_id = fields.Many2one("res.tempat.muat", string="Tempat Muat", tracking=True)
    tujuan_bongkar_id = fields.Many2one("res.tujuan.bongkar", string="Tujuan Bongkar", tracking=True)
    
    state = fields.Selection([('draft', _('Draft')), 
                              ('to_bill', _('To Bill')),
                              ('complete', _('Complete')), 
                              ('cancel', _('Cancelled'))], string='Status', default='draft', tracking=True)
    
    line_ids = fields.One2many('delivery.note.line', 'delivery_note_id', string='Delivery Note Items')
    sale_order_count = fields.Integer(string='Sale Order Count', compute='_compute_sale_order_count')
    origin = fields.Char(string='Source Document', tracking=True)
    notes = fields.Html(string='Notes', tracking=True)
    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders', compute='_compute_sale_ids', store=True)
    vehicle_category_id = fields.Many2one('fleet.vehicle.model.category', string='Vehicle Category', related='fleet_id.category_id', store=True)


    @api.depends('line_ids')
    def _compute_sale_ids(self):
        for rec in self:
            rec.sale_order_ids = rec.line_ids.sale_line_id.order_id


    @api.depends('line_ids')
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.line_ids.mapped('sale_line_id.order_id'))

    def action_view_sale_orders(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        sale_orders = self.line_ids.mapped('sale_line_id.order_id')
        if len(sale_orders) > 1:
            action['domain'] = [('id', 'in', sale_orders.ids)]
        elif len(sale_orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = sale_orders.id
        return action



    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            # if vals.get('sequence_id'):
            #     vals['name'] = self.env['ir.sequence'].browse(vals['sequence_id']).next_by_id() or _('New')
            # else:
            vals['name'] = self.env['ir.sequence'].next_by_code('delivery.note') or _('New')
        return super(DeliveryNote, self).create(vals)
    
   
    
    def action_confirm(self):
        not_draft_self = self.filtered(lambda x: x.state != 'draft')
        if not_draft_self:
            raise UserError(_('Only draft delivery notes can be confirmed.'))
        self.write({'state': 'to_bill'})

    def action_complete(self):
        self_with_to_bill = self.filtered(lambda x: x.state == 'to_bill')
        if not self_with_to_bill:
            raise UserError(_('Only delivery notes in to bill state can be completed.'))
        
        self_with_no_transport_receipt = self_with_to_bill.filtered(lambda x: not x.transport_receipt_no)
        self_with_no_delivery_date = self_with_to_bill.filtered(lambda x: not x.delivery_finish_date)
        self_with_no_tempat_muat = self_with_to_bill.filtered(lambda x: not x.tempat_muat_id)
        self_with_no_tujuan_bongkar = self_with_to_bill.filtered(lambda x: not x.tujuan_bongkar_id)

        if self_with_no_transport_receipt:
            raise UserError(_('Transport Receipt No. is required for completing delivery notes. Please fill for %s' % ', '.join(self_with_no_transport_receipt.mapped('name'))))
        if self_with_no_delivery_date:
            raise UserError(_('Delivery Finish Date is required for completing delivery notes. Please fill for %s' % ', '.join(self_with_no_delivery_date.mapped('name'))))

        if self_with_no_tempat_muat:
            raise UserError(_('Tempat Muat is required for completing delivery notes. Please fill for %s' % ', '.join(self_with_no_tempat_muat.mapped('name'))))
        if self_with_no_tujuan_bongkar:
            raise UserError(_('Tujuan Bongkar is required for completing delivery notes. Please fill for %s' % ', '.join(self_with_no_tujuan_bongkar.mapped('name'))))
        
        
        self_with_to_bill.write({'state': 'complete'})
    
    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a delivery note that is not in draft state.'))
        return super(DeliveryNote, self).unlink()
    
    def action_change_sale_order(self):
        partner_ids = self.partner_id.ids
        if len(partner_ids) != 1:
            raise UserError(_('You can only change sale order for 1 customer.'))


        return {
            'name': _('Change Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.change.sale.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_delivery_note_ids': self.ids,
            },
        }

   


class DeliveryNoteLine(models.Model):
    _name = 'delivery.note.line'
    _description = 'Delivery Note Line'
    _rec_name = "product_id"


    delivery_note_id = fields.Many2one('delivery.note', string='Delivery Note', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('delivery_note_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', compute='_compute_product_uom', store=True, 
                                  
                                  readonly=False,domain="[('category_id', '=', product_uom_category_id)]")
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount', store=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    other_quantity = fields.Float(string='Other Quantity')
    other_uom_id = fields.Many2one('uom.uom', string='Other UOM')
    sale_order_id = fields.Many2one('sale.order',)
    no_container = fields.Char("No. Container")

    # @api.model
    # def create(self, vals):
    #     if vals.get('sale_order_id') and not vals.get('sale_line_id'):
    #         sale_order = self.env['sale.order'].browse(vals['sale_order_id'])
    #         line_id = sale_order.order_line.filtered(lambda line: line.product_id.id == vals['product_id'])
    #         if line_id:
    #             vals['sale_line_id'] = line_id[0].id
    #     return super(DeliveryNoteLine, self).create(vals)
    
    def write(self, vals):
        if vals.get('sale_order_id'):
            for line in self:
                sale_order = self.env['sale.order'].browse(vals['sale_order_id'])
                product_id = vals.get('product_id', line.product_id.id)

                line_id = sale_order.order_line.filtered(lambda line: line.product_id.id == product_id)
                if line_id:
                    vals['sale_line_id'] = line_id[0].id
                else:
                    product_id = self.env['product.product'].browse(product_id)
                    raise UserError(_('Product %s is not in Sale Order %s' % (product_id.name, sale_order.name)))
        return super(DeliveryNoteLine, self).write(vals)

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit


