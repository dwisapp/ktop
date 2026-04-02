from odoo.http import request
from odoo import http, _
import json
import uuid
from datetime import datetime, timedelta
from odoo.exceptions import AccessDenied, UserError, ValidationError
from odoo.tools.image import image_data_uri
import base64
from werkzeug.exceptions import Forbidden, NotFound
from ast import literal_eval
from math import ceil
import jwt



class Session(http.Controller):



    # @http.route("/api/session/auth", type="json", auth="none", methods=["POST"], csrf=False)
    # def session_auth(self, **kwargs):
    #     email = kwargs.get("email", None)
    #     password = kwargs.get("password", None)
    #     if not email or not password:
    #         raise UserError("Harap Lengkapi Email dan Password")
    #     try:
    #         uid = request.session.authenticate(request.session.db, email, password)
    #     except AccessDenied as e:
    #         raise UserError("Username dan password yang anda masukkan tidak sesuai")
    #     key = str(uuid.uuid4())
    #     request.env["auth.api.key"].sudo().create({"name": "Login " + email + " "+ (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
    #                                         "key": key, 
    #                                         "user_id": uid,
    #                                         })
    #     return {
    #         "authorization_key": key,
    #     }

    @http.route("/api/session/auth", type="json", auth="none", methods=["POST"], csrf=False)
    def session_auth(self, **kwargs):
        email = kwargs.get("email")
        password = kwargs.get("password")
        if not email or not password:
            raise UserError("Harap Lengkapi Email dan Password")

        try:
            uid = request.session.authenticate(request.session.db, email, password)
        except AccessDenied:
            raise UserError("Username dan password yang anda masukkan tidak sesuai")

        # Ambil secret dari config (contoh hardcode, ganti dengan config aman)
        jwt_secret = request.env['ir.config_parameter'].sudo().get_param('jwt_secret_key')

        # Buat payload JWT
        payload = {
            "user_id": uid,
            "jti": str(uuid.uuid4()),
            "exp": datetime.now() + timedelta(days=7),
            "iat": datetime.now(),
        }

        token = jwt.encode(payload, jwt_secret, algorithm="HS256")

        return {
            "authorization_key": token,
            
        }


    @http.route("/api/session/logout", type="json", auth="jwt", methods=["POST"])
    def session_logout(self):
        # Ambil token dari header Authorization Bearer
        auth_header = request.httprequest.environ.get("HTTP_AUTHORIZATION")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValidationError("Authorization header tidak ditemukan atau tidak valid.")
        
        token = auth_header[7:]  

        jwt_secret = request.env['ir.config_parameter'].sudo().get_param('jwt_secret_key')
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            jti = payload.get("jti")
            exp = payload.get("exp")
            if not jti or not exp:
                raise ValidationError("Token tidak valid: jti atau exp tidak ditemukan.")
        except jwt.ExpiredSignatureError:
            raise ValidationError("Token telah kedaluwarsa.")
        except jwt.InvalidTokenError:
            raise ValidationError("Token tidak valid.")

        blacklist_model = request.env["jwt.token.blacklist"].sudo()
        blacklist_model.create({
            "jti": jti,
            "expired_at": datetime.fromtimestamp(exp),
        })

        request.session.logout()

        return "Logout successful"
    

    @http.route("/api/user/reset-password", type="json", auth="none", methods=["POST"], csrf=False)
    def reset_password(self, **kwargs):
        email = kwargs.get("email", None)
        if not email:
            return {
                "status": "error",
                "message": "Email is empty",
            }
        user = request.env["res.users"].sudo().search([("login", "=", email)])
        if not user:
            return {
                "status": "error",
                "message": "Email not found",
            }
        user.action_reset_password()
        return {
            "status": "success",
        }
    
    
    def _prepare_user_vals(self, user):
        employee = user.employee_ids and user.employee_ids[0] or request.env["hr.employee"]

        return {
            "name": user.name or "",
            "email": user.login or "",
            "phone": user.phone or "",
            "street": user.street or "",
            "city": user.city or "",
            "province": {
                "code": user.state_id.code or "",
                "name": user.state_id.name or "",
            },
            "country": {
                "code": user.country_id.code or "",
                "name": user.country_id.name or "",
            },
            "job_title": employee.job_id.name or "",
            "department" : employee.department_id.name or "",
            "manager" : employee.parent_id.name or "",
            "badge" : employee.barcode or "",

        }

    @http.route("/api/user", type="json", auth="jwt", methods=["GET"])
    def get_user(self):
        user = request.env.user
        vals = self._prepare_user_vals(user)
        return {
                "user": vals
            }
        

    
    
    @http.route("/api/user", type="json", auth="jwt", methods=["PUT"])
    def update_user(self, **kwargs):
        user = request.env.user
        vals = self._prepare_update_user(user, kwargs)
        if vals.get('status') == "success":
            user.write(vals['vals'])
        else:
            raise UserError(vals['message'])
        return {
            "user": self._prepare_user_vals(user)
        }

    def _prepare_update_user(self, user, vals):
        email = vals.get("email", None)
        phone = vals.get("phone", None)
        street = vals.get("street", None)
        city = vals.get("city", None)
        state = vals.get("province", None)
        country = vals.get("country", None)
        name = vals.get("name", None)
        
        country_id = user.country_id
        write_vals = {
            'status': "success",
            'vals': {}
        }
        if email:
            write_vals['vals']["login"] = email
            write_vals['vals']["email"] = email
        if phone:
            write_vals['vals']["phone"] = phone
        if street:
            write_vals['vals']["street"] = street
        if city:
            write_vals['vals']["city"] = city
        if country:
            country_id = request.env["res.country"].sudo().search([("code", "=", country)])
            if country_id:
                write_vals['vals']["country_id"] = country_id.id
                
        if state:
            state_id = request.env["res.country.state"].sudo().search([("code", "=", state), ("country_id", "=", country_id.id)])
            if state_id:
                write_vals['vals']["state_id"] = state_id.id
        if name:
            write_vals['vals']["name"] = name
        return write_vals
   

    @http.route("/api/user/password", type="json", auth="jwt", methods=["PUT"])
    def update_password(self, **kwargs):
        old_password = kwargs.get("old_password", None)
        new_password = kwargs.get("new_password", None)
        user = request.env.user
        if old_password and new_password:

            try:
                request.env['res.users'].change_password(old_password, new_password)
                return {}
            except AccessDenied as e:
                raise UserError("Password lama tidak sesuai")
            except UserError as e:
                raise UserError(e)
            
        else:
            raise UserError("Password lama dan baru tidak boleh kosong")
        
    
    

    @http.route("/api/delete/account", type="json", auth="jwt", methods=["DELETE"], csrf=False)
    def delete_account(self):
        user = request.env.user
        user._deactivate_portal_user()
        user.auth_api_key_ids.unlink()
        return {}