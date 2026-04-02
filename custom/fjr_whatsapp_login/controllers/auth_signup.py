from random import choice
import string

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import uuid

class AuthSignUpHome(Home):


    @http.route()
    def web_auth_signup(self, *args, **kw):
        phone_number = kw.get('whatsapp_number', False)
        qcontext = {}
        
        # if "otp_login" in kw:
        qcontext["otp_login"] = True


        if request.httprequest.method == 'POST' and phone_number:
            phone_to_search = phone_number
            if phone_number.startswith("0"):
                phone_to_search = "+62" + phone_number[1:]
            elif phone_number.startswith("62"):
                phone_to_search = "+" + phone_number
            partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_to_search)

            otp_verification = request.env['otp.verification'].sudo().search([('phone', '=', phone_number)], order="create_date desc", limit=1)
            try:
                otp = str(kw.get('otp'))
                if otp_verification.otp == otp and not partner_id:
                    password = str(uuid.uuid4())[0:15]
                    qcontext.update({'login': phone_number,
                                    'password': password,
                                     'confirm_password': password,
                                     'is_no_password': True,
                                     'whatsapp_number': phone_to_search,
                                     })
                    kw.update({
                        'login' :phone_number,
                        'password': password,
                        'confirm_password': password,
                        'is_no_password': True

                    })
                    
                else:
                    qcontext['login'] = ''
                    qcontext['password'] = ''
                    qcontext['otp_login'] = True
                    qcontext['whatsapp_number'] = phone_number
                    qcontext['is_send_otp'] = True

                    if partner_id:
                        qcontext['error'] = "Phone Number already registered"
                    elif otp_verification.otp != otp:
                        qcontext['error'] = "Wrong OTP"
            except UserError as e:
                qcontext['error'] = e.name or e.value
        request.params.update(qcontext)

        response = super(AuthSignUpHome, self).web_auth_signup(*args, **kw)
        response.qcontext.update(qcontext)
                        

        return response
    
    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignUpHome, self).get_auth_signup_qcontext()
        qcontext['whatsapp_number'] = request.params.get('whatsapp_number', False)
        qcontext['is_send_otp'] = request.params.get('is_send_otp', False)
        qcontext['otp_login'] = request.params.get('otp_login', False)
        qcontext['is_no_password'] = request.params.get('is_no_password', False)
        return qcontext


    def _prepare_signup_values(self, qcontext):
        values = super(AuthSignUpHome, self)._prepare_signup_values(qcontext)
        values['is_no_password'] = qcontext.get('is_no_password', False)
        values['phone'] = qcontext.get('whatsapp_number', False)
        return values