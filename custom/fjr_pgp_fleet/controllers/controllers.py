from odoo import http
from werkzeug.exceptions import NotFound
from odoo.http import request


class HRExpenseSheet(http.Controller):

    @http.route('/fleet/document/loan/<string:approval_type>/<string:token>/<int:user_id>', auth='public', methods=['GET'])
    def manager_approval(self,user_id,approval_type,token, **kwargs):
        sheet = request.env['fleet.document.loan'].sudo().search([('public_token', '=', token)])
        if not sheet:
            return NotFound()
        call_back = False
        
        message = "Loan Approved"
        sheet = sheet.with_user(user_id)
        if approval_type == 'approve':
                sheet.action_approve()
            
        elif approval_type == 'reject':
            # user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        
            # sheet._do_refuse("Refused by %s" % user.name or user_type)
            message = "Please Enter Refuse Reason"
            call_back = "/fleet/document/loan/json/%s/%s/%s" % (user_id, approval_type, token)
        
        return request.render('fjr_kasir_base.base_auto_close', {'message': message, 'callback': call_back})
    

    @http.route('/fleet/document/loan/json/<int:user_id>/<string:approval_type>/<string:token>', auth='public', methods=['POST'], type='json', csrf=False)
    def refuse_reason(self, user_id, approval_type, token, **kwargs):
        loan = request.env['fleet.document.loan'].sudo().search([('public_token', '=', token)])
        if not loan:
            return NotFound()
        loan = loan.with_user(user_id)
        loan._do_reject(kwargs.get('userInput'))
        return {'status': 'ok'}



        
        
   