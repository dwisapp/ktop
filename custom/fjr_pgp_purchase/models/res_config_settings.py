from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_order_approval_ids = fields.Many2many('purchase.order.approval', related='company_id.purchase_order_approval_ids', string='Purchase Order Approval', readonly=False)
    purchase_order_approval_whatsapp_template_id = fields.Many2one('whatsapp.template', related='company_id.purchase_order_approval_whatsapp_template_id', string='Whatsapp Template', readonly=False)
  