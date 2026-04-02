from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    other_quantity = fields.Float(string='Other Quantity', compute='_compute_other_quantity', store=True, readonly=False)
    other_uom_id = fields.Many2one('uom.uom', string='Other UOM', compute='_compute_other_quantity', store=True, readonly=False)


    @api.model
    def create(self,vals):
        res = super(AccountMoveLine, self).create(vals)
        source_orders = res.move_id.line_ids.sale_line_ids.order_id
        context_order = self._context.get('sale_order_origin', False)
        if not res.sale_line_ids and res.move_id.is_invoice():
            if context_order:
                sale_order_id = self.env['sale.order'].browse(context_order)
                same_product_line = sale_order_id.order_line.filtered(lambda line: line.product_id == res.product_id)
                if same_product_line:
                    res.sale_line_ids = [(4, same_product_line.ids[0])]

            elif source_orders:
                same_product_line = source_orders.order_line.filtered(lambda line: line.product_id == res.product_id)
                if same_product_line:
                    res.sale_line_ids = [(4, same_product_line.ids[0])]
            
        return res


    @api.depends('sale_line_ids.delivery_note_line_ids.other_quantity')
    def _compute_other_quantity(self):
        for line in self:
            line.other_quantity = sum(line.sale_line_ids.delivery_note_line_ids.mapped('other_quantity'))
            line.other_uom_id = line.sale_line_ids.delivery_note_line_ids[0].other_uom_id.id if line.sale_line_ids.delivery_note_line_ids.other_uom_id else False
    


