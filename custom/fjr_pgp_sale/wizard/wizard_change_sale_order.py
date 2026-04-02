from odoo import models, fields, api, _


class WizardChangeSaleOrder(models.TransientModel):
    _name = 'wizard.change.sale.order'
    _description = 'Wizard Change Sale Order'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    delivery_note_ids = fields.Many2many('delivery.note', string='Delivery Note', required=True)

    def action_change(self):
        for dn in self.delivery_note_ids:
            old_sale_order_ids = dn.sale_order_ids
            message = _('Sale Order changed from %s to %s', ', '.join(old_sale_order_ids.mapped('name')), self.sale_order_id._get_html_link())
            dn.message_post(body=message)

        self.delivery_note_ids.line_ids.write({'sale_order_id': self.sale_order_id.id})


