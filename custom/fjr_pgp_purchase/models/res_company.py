from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_order_approval_ids = fields.Many2many('purchase.order.approval',string='Purchase Order Approval')
    purchase_order_approval_whatsapp_template_id = fields.Many2one('whatsapp.template',string='Whatsapp Template')