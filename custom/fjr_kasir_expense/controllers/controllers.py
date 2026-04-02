from odoo import http
from werkzeug.exceptions import NotFound
from odoo.http import request


class HRExpenseSheet(http.Controller):

    @http.route('/expense/<string:user_type>/<int:user_id>/<string:approval_type>/<string:token>', auth='public', methods=['GET'])
    def manager_approval(self, user_type,user_id,approval_type,token, **kwargs):
        sheet = request.env['hr.expense.sheet'].sudo().search([('public_token', '=', token)])
        if not sheet:
            return NotFound()
        call_back = False
        
        message = "Expense Approved"
        sheet = sheet.with_user(user_id)
        if approval_type == 'approve':
            if user_type == 'manager':
                sheet._do_approve()
            elif user_type == 'accounting' or user_type == 'accounting_manager':
                sheet.action_approved_accounting_manager()
            elif user_type == 'payment':
                sheet.action_approve_payout()
        elif approval_type == 'refuse':
            # user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        
            # sheet._do_refuse("Refused by %s" % user.name or user_type)
            message = "Please Enter Refuse Reason"
            call_back = "/expense/json/%s/%s/%s/%s" % (user_type, user_id, approval_type, token)
        
        return request.render('fjr_kasir_base.base_auto_close', {'message': message, 'callback': call_back})
    

    @http.route('/expense/json/<string:user_type>/<int:user_id>/<string:approval_type>/<string:token>', auth='public', methods=['POST'], type='json', csrf=False)
    def refuse_reason(self, user_type, user_id, approval_type, token, **kwargs):
        sheet = request.env['hr.expense.sheet'].sudo().search([('public_token', '=', token)])
        if not sheet:
            return NotFound()
        sheet = sheet.with_user(user_id)
        sheet._do_refuse(kwargs.get('userInput'))
        return {'status': 'ok'}



        
        
   