from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    jenis_barang = fields.Char("Jenis Barang")
    tempat_muat = fields.Char("Detail Tempat Muat")
    tempat_muat_id = fields.Many2one("res.tempat.muat", string="Tempat Muat")
    tujuan_bongkar = fields.Char("Detail Tujuan Bongkar")
    tujuan_bongkar_id = fields.Many2one("res.tujuan.bongkar", string="Tujuan Bongkar")
    kapal_id = fields.Many2one('kapal.kapal', string='Kapal') 
    display_button_create_delivery_note = fields.Boolean(string='Display Delivery Note Button', compute='_compute_display_button_create_delivery_note')
    delivery_note_count = fields.Integer(string='Delivery Note Count', compute='_compute_delivery_note_count')

    @api.depends('order_line.delivery_note_line_ids')
    def _compute_delivery_note_count(self):
        for order in self:
            order.delivery_note_count = len(order.order_line.delivery_note_line_ids.delivery_note_id)

    @api.depends('order_line.qty_delivered_method', 'order_line.qty_to_deliver')
    def _compute_display_button_create_delivery_note(self):
        for order in self:
            delivery_note_line = order.order_line.filtered(lambda line: line.qty_delivered_method == 'delivery_note')
            order.display_button_create_delivery_note = bool(delivery_note_line)

    def action_view_delivery_notes(self):
        action = self.env['ir.actions.act_window']._for_xml_id('fjr_pgp_sale.delivery_note_action')
        delivery_notes = self.order_line.delivery_note_line_ids.delivery_note_id
        if len(delivery_notes) > 1:
            action['domain'] = [('id', 'in', delivery_notes.ids)]
        elif len(delivery_notes) == 1:
            action['views'] = [(self.env.ref('fjr_pgp_sale.delivery_note_view_form').id, 'form')]
            action['res_id'] = delivery_notes.id
        return action

    def action_create_delivery_note(self):
        delivery_notes = self.env['delivery.note']
        for rec in self:
            delivery_note = delivery_notes.create(rec._prepare_delivery_note_vals())
            delivery_notes |= delivery_note
        action = self.env["ir.actions.actions"]._for_xml_id("fjr_pgp_sale.delivery_note_action")
        if len(delivery_notes) == 1:
            action['res_id'] = delivery_notes.id
            action['views'] = [(self.env.ref('fjr_pgp_sale.delivery_note_view_form').id, 'form')]
        else:
            action['domain'] = [('id', 'in', delivery_notes.ids)]
        return action
    


    def _prepare_delivery_note_vals(self):
        return {
            'jenis_barang': self.jenis_barang,
            'tempat_muat': self.tempat_muat,
            'tujuan_bongkar': self.tujuan_bongkar,
            'partner_id': self.partner_id.id,
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': max(line.qty_to_deliver, 0),
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'sale_line_id': line.id,
                'sale_order_id': self.id,
            }) for line in self.order_line.filtered(lambda line: line.qty_delivered_method == 'delivery_note')],
        }


    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['kapal_id'] = self.kapal_id.id
        return invoice_vals
    
    def action_view_invoice(self, invoices=False):
        action = super(SaleOrder, self).action_view_invoice(invoices)
        if len(self) == 1:
            action['context']['sale_order_origin'] = self.id
        return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    delivery_date = fields.Datetime(string='Delivery Date')
    delivery_note_ok = fields.Boolean(string='Can be Delivery Note', related='product_id.delivery_note_ok')
    qty_delivered_method = fields.Selection(selection_add=[('delivery_note', 'Delivery Note')])
    delivery_note_line_ids = fields.One2many('delivery.note.line', 'sale_line_id', string='Delivery Note Line')
    other_quantity = fields.Float(string='Other Quantity')
    other_uom_id = fields.Many2one('uom.uom', string='Other UOM')

    @api.depends('delivery_date')
    def _compute_qty_at_date(self):
        super(SaleOrderLine, self)._compute_qty_at_date()
        for line in self.filtered(lambda line: line.delivery_date):
            line.scheduled_date = line.delivery_date

    @api.depends('product_id')
    def _compute_qty_delivered_method(self):
        """ Stock module compute delivered qty for product [('type', 'in', ['consu', 'product'])]
            For SO line coming from expense, no picking should be generate: we don't manage stock for
            those lines, even if the product is a storable.
        """
        super(SaleOrderLine, self)._compute_qty_delivered_method()
        for line in self:
            if line.product_id.delivery_note_ok:
                line.qty_delivered_method = 'delivery_note'

    @api.depends('delivery_note_line_ids.product_uom_qty', 'delivery_note_line_ids.delivery_note_id.state')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()
        for line in self.filtered(lambda line: line.qty_delivered_method == 'delivery_note'):
            qty = 0.0
            for delivery_note_line in line.delivery_note_line_ids.filtered(lambda l: l.delivery_note_id.state != 'cancel'):
                qty += delivery_note_line.product_uom._compute_quantity(delivery_note_line.product_uom_qty, line.product_uom)
            line.qty_delivered = qty


    @api.depends('qty_delivered_method')
    def _compute_qty_to_deliver(self):
        super(SaleOrderLine, self)._compute_qty_to_deliver()
        for line in self.filtered(lambda line: line.qty_delivered_method == 'delivery_note'):
            line.display_qty_widget = line.state in ('draft', 'sent', 'sale') 
    
    @api.depends('state')
    def _compute_product_uom_readonly(self):
        super(SaleOrderLine, self)._compute_product_uom_readonly()  
        for line in self:
            # line.ids checks whether it's a new record not yet saved
            line.product_uom_readonly = line.ids and line.state in ['cancel']