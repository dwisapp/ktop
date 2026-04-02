from odoo import models, fields, api, _
import uuid


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('rejected', 'Rejected')])
    approval_line_ids = fields.One2many('purchase.order.approval.line', 'order_id', string='Approval', compute='_compute_approval_ids', store=True)
    can_approve = fields.Boolean(compute='_compute_can_approve')
    public_token = fields.Char('Public Token', copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', copy=False)
    



    @api.depends('approval_line_ids.state')
    def _compute_can_approve(self):
        for order in self:
            order.can_approve = False
            if order.approval_line_ids.filtered(lambda x: x.state not in ['approved', 'rejected'] and self.env.user in x.user_ids):
                order.can_approve = True


    @api.depends('company_id.po_double_validation', 'amount_total')
    def _compute_approval_ids(self):
        for order in self:
            approval_line = [(5, 0, 0)]
            if order.company_id.po_double_validation == 'one_step':
                order.approval_line_ids = approval_line
                continue
            approval_ids = order.company_id.purchase_order_approval_ids.filtered(lambda x: x.min_amount <= order.amount_total)
            approval_ids = approval_ids.sorted(key=lambda x: x.min_amount)
            sequence = 1
            for approval_id in approval_ids:
                approval_line.append((0, 0, {
                    'approval_id': approval_id.id,
                    'sequence': sequence,
                    'user_ids': [(6, 0, approval_id.user_ids.ids)],
                    'min_amount': approval_id.min_amount
                }))
                sequence += 1
            order.approval_line_ids = approval_line

    def _approval_allowed(self):
        approval_lines = self.approval_line_ids.filtered(lambda x: x.state not in ['approved', 'rejected'])
        if not approval_lines:
            self.write({'public_token': False})
            return True
        
        approval_has_user = approval_lines.filtered(lambda x: self.env.user in x.user_ids)
        if not approval_has_user:
            self._send_whatsapp_for_approve()
            return False
        
        approval_has_user.write({'state': 'approved', 'user_id': self.env.user.id, 'date': fields.Datetime.now()})
        not_approved = approval_lines.filtered(lambda x: x.state != 'approved')   
        
        if not_approved:
            self._send_whatsapp_for_approve(not_approved)
            return False
        self.write({'public_token': False})

        return True
    

    def _approval_allowed_from_url(self, user_id):
        approval_lines = self.approval_line_ids.filtered(lambda x: x.state not in ['approved', 'rejected'] and user_id in x.user_ids.ids)
        if not approval_lines:
            return False
        
        return True


    def _reject_allowed_from_url(self, user_id):
        approval_lines = self.approval_line_ids.filtered(lambda x: x.state not in ['approved', 'rejected'] and user_id in x.user_ids.ids)
        if not approval_lines:
            return False
        
        return True
    

    def action_reject(self):
        global_reason = self._context.get('global_reason', False)
        if not global_reason:
            return {
                'name': _('Reject Reason'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'wizard.global.reason',
                'target': 'new',
                'context': {
                    'default_model': self._name,
                    'default_res_id': str(self.ids),
                    'default_action_name': 'action_reject'
                }
            }
        approval_lines = self.approval_line_ids.filtered(lambda x: x.state not in ['approved', 'rejected'] and self.env.user in x.user_ids)
        approval_lines.write({'state': 'rejected', 'user_id': self.env.user.id, 'reason': global_reason, 'date': fields.Datetime.now()})
        self.write({'state': 'rejected', 'public_token': False})

    

    def _send_whatsapp_for_approve(self, approval_lines=False):
        if not approval_lines:
            approval_lines = self.approval_line_ids

        if not self.public_token:
            public_token = uuid.uuid4().hex
            self.write({'public_token': public_token})
        
        approval_url = f"/purchase_order/approve/{self.public_token}"
        rejection_url = f"/purchase_order/reject/{self.public_token}"
        wizard_approval = self.env['purchase.order.approval.line.per.user']

        approval_lines = approval_lines.filtered(lambda x: not x.is_send_whatsapp)
        if approval_lines:
            for user in approval_lines.user_ids:
                wizard_approval |= wizard_approval.create({
                    'user_id': user.id,
                    'order_id': self.id,
                    'approval_link': approval_url + f"/{user.id}",
                    'rejection_link': rejection_url + f"/{user.id}"
                })
            wizard_approval._send_whatsapp_template()
            approval_lines.write({'is_send_whatsapp': True})


        

    def button_draft(self):
        self.approval_line_ids.write({'state': 'draft', 'user_id': False, 'reason': False, 'date': False, 'is_send_whatsapp': False})
        return super(PurchaseOrder, self).button_draft()
    
    def button_cancel(self):
        for order in self:
            for move in order.order_line.move_ids.filtered(lambda move: move.state == 'done'):
                move.move_line_ids.write({'quantity': 0})
                move.write({'state': 'cancel'})
        return super(PurchaseOrder, self).button_cancel()

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('order_id.analytic_account_id')
    def _compute_analytic_distribution(self):
        for line in self:
            line.analytic_distribution = {line.order_id.analytic_account_id.id: 100}


class PurchaseOrderApprovalLine(models.Model):
    _name = 'purchase.order.approval.line'
    _description = 'Purchase Order Approval Line'
    _order = 'sequence, id'


    sequence = fields.Integer(string='Sequence')
    order_id = fields.Many2one('purchase.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    approval_id = fields.Many2one('purchase.order.approval', string='Approval', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', copy=False, readonly=True)
    user_ids = fields.Many2many('res.users', string='User', required=True)
    min_amount = fields.Float(string='Minimum Amount')
    reason = fields.Text(string='Reason')
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True)
    date = fields.Datetime(string='Date')
    is_send_whatsapp = fields.Boolean('Is Send Whatsapp', default=False)
    

    def _action_approve(self, user_id):
        self.write({'state': 'approved', 'user_id': user_id})


    def _action_reject(self, user_id, reason):
        self.write({'state': 'rejected', 'user_id': user_id, 'reason': reason})

    


class PurchaseOrderApprovalLinePerUser(models.TransientModel):
    _name = 'purchase.order.approval.line.per.user'
    _description = 'Purchase Order Approval Line Per User'

    user_id = fields.Many2one('res.users', string='User', required=True)
    order_id = fields.Many2one('purchase.order', string='Order Reference', required=True)
    approval_link = fields.Char('Approval Link', copy=False)
    rejection_link = fields.Char('Rejection Link', copy=False)


    def _send_whatsapp_template(self):
        context = dict(self._context)
        context.update({
            'active_model': 'purchase.order.approval.line.per.user',
            'active_ids': self.ids,
            'no_partner_notification': True,
        })
        if self.order_id.company_id.purchase_order_approval_whatsapp_template_id:
            context.update({
                'default_wa_template_id': self.order_id.company_id.purchase_order_approval_whatsapp_template_id.id
            })
        whatsapp_compose = self.env['whatsapp.composer'].with_context(context).create({
            'res_model': 'purchase.order.approval.line.per.user',
            'res_ids': str(self.ids),
        })
        whatsapp_compose._send_whatsapp_template()