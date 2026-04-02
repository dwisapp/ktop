from odoo import models, fields, api, _

class WizardChangeSaleOrder(models.TransientModel):
    _inherit = 'wizard.change.sale.order'

    def action_change(self):
        self.delivery_note_ids.uang_jalan_ids.write({'sale_order_id': self.sale_order_id.id})
        return super(WizardChangeSaleOrder, self).action_change()