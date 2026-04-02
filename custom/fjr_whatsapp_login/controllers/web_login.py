from random import choice
import string

from odoo.addons.web.controllers.home import Home, ensure_db
from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request


class OtpLoginHome(Home):


    @http.route()
    def web_login(self, *args, **kw):
        
        phone_number = kw.get('whatsapp_number', False)
        qcontext = {}
        
        if "otp_login" in kw:
            qcontext["otp_login"] = True
        if request.httprequest.method == 'POST' and phone_number:
            otp_verification = request.env['otp.verification'].sudo().search([('phone', '=', phone_number)], order="create_date desc", limit=1)
            try:
                otp = str(kw.get('otp'))
                if otp_verification.otp == otp:
                    user_id = otp_verification.user_id
                    if user_id:
                        request.env.cr.execute(
                            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                            [user_id.id]
                        )
                        hashed = request.env.cr.fetchone()[0]
                        qcontext.update({'login': user_id.sudo().login,
                                    'name': user_id.sudo().partner_id.name,
                                    'password': hashed + 'mobile_otp_login' })
                        kw.update({
                            'login' : user_id.sudo().login,
                            'password': hashed + 'mobile_otp_login'

                        })
                    
                else:
                    qcontext['login'] = ''
                    qcontext['password'] = ''
                    qcontext['error'] = "Wrong OTP"
                    qcontext['otp_login'] = True
                    qcontext['whatsapp_number'] = phone_number
                    qcontext['is_send_otp'] = True
            except UserError as e:
                qcontext['error'] = e.name or e.value
        request.params.update(qcontext)

        response = super(OtpLoginHome, self).web_login(*args, **kw)
        response.qcontext.update(qcontext)
                        

        return response
    

    @http.route('/otp-verification/whatsapp', type='json', auth='public')
    def create_otp_whatsapp(self, **kw):
        otp_type = kw.get('type', 'login')
        phone_number = kw.get('phone_number')
        if not phone_number:
            return {
                'status' : 'error',
                'message' : 'No account registered with that phone number'
            }
        phone_to_search = phone_number
        if otp_type == 'login':
            if phone_number.startswith("0"):
                phone_to_search = "+62" + phone_number[1:]
            elif phone_number.startswith("62"):
                phone_to_search = "+" + phone_number
            partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_to_search)
            user_ids = partner_id.mapped('user_ids')
            user_id = user_ids[0].sudo() if user_ids else False
            if user_id:
                OTP = self.generate_otp(4)
                vals = {
                    'otp': OTP,
                    'phone': phone_number,
                    'otp_type' : otp_type,
                    'user_id': user_id.id
                }
                otp = request.env['otp.verification'].sudo().create(vals)
                
            else:
                return {
                'status' : 'error',
                'message' : 'No account registered with that phone number'
            }
        elif otp_type == 'register':
            if phone_number.startswith("0"):
                phone_to_search = "+62" + phone_number[1:]
            elif phone_number.startswith("62"):
                phone_to_search = "+" + phone_number
            partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_to_search)
            if partner_id:
                return {
                    'status' : 'error',
                    'message' : 'Account already registered with that phone number'
                }
            OTP = self.generate_otp(4)
            vals = {
                'otp': OTP,
                'phone': phone_number,
                'otp_type' : otp_type,
            }
            otp = request.env['otp.verification'].sudo().create(vals)
           
        return {
                    'status' : 'success'
                }


    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp