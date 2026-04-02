from odoo import http
from werkzeug.exceptions import NotFound
from odoo.http import request


class PurchaseOrderApproval(http.Controller):

    @http.route('/purchase_order/<string:approval_type>/<string:token>/<int:user_id>', auth='public', methods=['GET'])
    def manager_approval(self,user_id,approval_type,token, **kwargs):
        purchase = request.env['purchase.order'].sudo().search([('public_token', '=', token)])
        if not purchase:
            return NotFound()
        call_back = False
        
        message = "Purchase Order Approved"
        purchase = purchase.with_user(user_id)
        if approval_type == 'approve':
            approval_allowed = purchase._approval_allowed_from_url(user_id)
            if not approval_allowed:
                message = "You are not allowed to approve this Purchase Order"
            else:
                purchase.button_approve()
            
        elif approval_type == 'reject':
            # user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        
            # sheet._do_refuse("Refused by %s" % user.name or user_type)
            reject_allowed = purchase._reject_allowed_from_url(user_id)
            if reject_allowed:
                message = "Please Enter Refuse Reason"
                call_back = "/purchase_order/json/%s/%s/%s" % (user_id, approval_type, token)
            
            else:
                message = "You are not allowed to reject this Purchase Order"
        
        return request.render('fjr_kasir_base.base_auto_close', {'message': message, 'callback': call_back})
    

    @http.route('/purchase_order/json/<int:user_id>/<string:approval_type>/<string:token>', auth='public', methods=['POST'], type='json', csrf=False)
    def refuse_reason(self, user_id, approval_type, token, **kwargs):
        purchase_order = request.env['purchase.order'].sudo().search([('public_token', '=', token)])
        if not purchase_order:
            return NotFound()
        purchase_order = purchase_order.with_user(user_id)
        print(kwargs.get('userInput'))
        purchase_order.with_context(global_reason=kwargs.get('userInput')).action_reject()
        return {'status': 'ok'}



        