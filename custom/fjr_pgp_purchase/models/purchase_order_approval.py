from odoo import models, fields, api, _


class PurchaseOrderApproval(models.Model):
    _name = 'purchase.order.approval'
    _description = 'Purchase Order Approval'

    name = fields.Char(string='Name', required=True)
    user_ids = fields.Many2many('res.users', string='Users')
    group_ids = fields.Many2many('res.groups', string='Groups')
    min_amount = fields.Float(string='Minimum Amount')
    company_id = fields.Many2one('res.company', string='Company')


    @api.onchange('group_ids')
    def _onchange_group_ids(self):
        self.user_ids = [(6, 0, self.group_ids.users.ids)]