from odoo import http
from odoo.http import request
import uuid
from odoo.addons.fjr_kasir_base.api.session import Session
from random import choice
import string
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class ApiLogin(Session):

    def _prepare_update_user(self, user, vals):
        phone_number = vals.get("phone", None)
        if phone_number:
            phone_number = phone_number
            if phone_number.startswith("0"):
                phone_number = "+62" + phone_number[1:]
            elif phone_number.startswith("62"):
                phone_number = "+" + phone_number
            elif phone_number.startswith("8"):
                phone_number = "+62" + phone_number
            partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_number)
            if partner_id and partner_id.id != user.partner_id.id:
                return {
                    'status': 'error',
                    'message': 'Phone number already registered',
                }
            vals['phone'] = phone_number
        return super()._prepare_update_user(user, vals)


    def _prepare_user_vals(self, user):
        result = super(ApiLogin,self)._prepare_user_vals(user)
        phone_number = result.get("phone", "")
        if phone_number.startswith("0"):
            phone_number = phone_number[1:]
        elif phone_number.startswith("62"):
            phone_number = phone_number[2:]
        elif phone_number.startswith("+62"):
            phone_number = phone_number[3:]
        result["phone"] = phone_number
        return result

    @http.route("/api/session/whatsapp/req-otp", type="json", auth="none", methods=["POST"], csrf=False)
    def session_auth_whatsapp(self, **kw):
        phone_number = kw.get("phone_number", False)
        if not phone_number:
            return {
                'status': 'error',
                'message': 'Phone number is required',
            }
        
        phone_to_search = phone_number
        if phone_number.startswith("0"):
            if phone_number[1:].startswith("8"):
                phone_to_search = "+62" + phone_number[1:]
            else:
                phone_to_search = "+62" + phone_number[2:]

        elif phone_number.startswith("62"):
            phone_to_search = "+" + phone_number
        partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_to_search)
        user_ids = partner_id.mapped('user_ids')
        user = user_ids[0].sudo() if user_ids else False
        if not user:
            return {
                'status': 'error',
                'message': 'No account registered with that phone number',
            }
        
        otp_verification = request.env["otp.verification"].sudo().create({
            "phone": phone_number,
            "otp": self.generate_otp(6),
            "otp_type": "login",
            "user_id": user.id,
        })
        return {
            'status': 'success',
            'message': 'OTP sent successfully',
            
        }
    
    @http.route("/api/session/auth/whatsapp", type="json", auth="none", methods=["POST"], csrf=False)
    def verify_otp_login(self, **kw):
        phone_number = kw.get("phone_number", False)
        otp = kw.get("otp", False)
        firebase_token = kw.get("firebase_token", False)
        if not phone_number:
            return {
                'status': 'error',
                'message': 'Phone number is required',
            }
        if not otp:
            return {
                'status': 'error',
                'message': 'OTP is required',
            }
        verification = request.env["otp.verification"].sudo().search([("phone", "=", phone_number), ("otp", "=", otp),("state", "=", "unverified")])
        if not verification:
            return {
                'status': 'error',
                'message': 'Invalid OTP',
            }
        key = str(uuid.uuid4())
        request.env["auth.api.key"].sudo().create({"name": "Login " + phone_number + " "+ (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                                            "key": key, 
                                            "user_id": verification.user_id.id,
                                            
                                            })
        verification.write({"state": "verified"})
        return {
            'status': 'success',
            'authorization_key': key
        }
    

    @http.route("/api/user/register/whatsapp/req-otp" , type="json", auth="none", methods=["POST"], csrf=False)
    def register_user_whatsapp(self, **kw):
        phone_number = kw.get("phone_number", False)
        if not phone_number:
            return {
                'status': 'error',
                'message': 'Phone number is required',
            }
        phone_to_search = phone_number
        if phone_number.startswith("0"):
            phone_to_search = "+62" + phone_number[1:]
        elif phone_number.startswith("62"):
            phone_to_search = "+" + phone_number
        partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_to_search)
        if partner_id:
            return {
                'status': 'error',
                'message': 'Account already registered with that phone number',
            }
        OTP = self.generate_otp(6)
        vals = {
            'otp': OTP,
            'phone': phone_number,
            'otp_type': 'register',
        }
        otp = request.env['otp.verification'].sudo().create(vals)
        return {
            'status': 'success',
            'message': 'OTP sent successfully',
        }
    
    @http.route("/api/user/register/whatsapp" , type="json", auth="none", methods=["POST"], csrf=False)
    def verify_otp_register(self, **kw):
        phone_number = kw.get("phone_number", False)
        email = kw.get("email", None)
        name = kw.get("name", None)
        otp = kw.get("otp", False)

        
        if email:
            user_id = request.env['res.users'].sudo().search([('login', '=', email)])
            if user_id:
                return {
                    'status': 'error',
                    'message': 'Email already registered with another account',
                }
       

        firebase_token = kw.get("firebase_token", None)
        if not phone_number:
            return {
                'status': 'error',
                'message': 'Phone number is required',
            }
        if not otp:
            return {
                'status': 'error',
                'message': 'OTP is required',
            }
        verification = request.env["otp.verification"].sudo().search([("phone", "=", phone_number), ("otp", "=", otp)])
        if not verification:
            return {
                'status': 'error',
                'message': 'Invalid OTP',
            }
        phone_to_create = phone_number
        if phone_number.startswith("0"):
            phone_to_create = "+62" + phone_number[1:]
        elif phone_number.startswith("62"):
            phone_to_create = "+" + phone_number
        

        partner = request.env["res.partner"].sudo().create({
            "name": name,
            "email": email,
            "phone": phone_to_create,
        })
        company_id = request.env["res.company"].sudo().search([], limit=1)
        base_root = request.env.ref("base.user_root")
        request.update_env(user=base_root)
        user = request.env["res.users"]._create_user_from_template(
                {
                    'partner_id': partner.id,
                    'login': email or phone_to_create,
                    'name': partner.name,
                    'password': str(uuid.uuid4()),
                    'is_no_password': True,
                })
        

        verification.write({"state": "verified"})
        key = str(uuid.uuid4())
        request.env["auth.api.key"].sudo().create({"name": "Login " + email + " "+ (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                                            "key": key, 
                                            "user_id": user.id,
                                            "firebase_token": firebase_token,
                                            })
        return {
            "status": "success",
            "authorization_key": key,
        }


    def _prepare_update_user(self, user, vals):
        res = super()._prepare_update_user(user, vals)
        if vals.get("phone"):
            phone_number = vals.get("phone")
            phone_number = phone_number
            if phone_number.startswith("0"):
                phone_number = "+62" + phone_number[1:]
            elif phone_number.startswith("62"):
                phone_number = "+" + phone_number
            partner_id = request.env['res.partner'].sudo()._search_on_phone_mobile("=", phone_number)
            
            if partner_id and partner_id.id != user.partner_id.id:
                return {
                    'status': 'error',
                    'message': 'Phone number already registered',
                }
            res['vals']['phone'] = phone_number
        return res

            
       



    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp