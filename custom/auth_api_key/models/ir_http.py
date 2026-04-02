# Copyright 2018 ACSONE SA/NV
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request
import jwt

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_api_key(cls):
        headers = request.httprequest.environ
        api_key = headers.get("HTTP_AUTHORIZATION")
        if api_key:
            request.update_env(user=1)
            auth_api_key = request.env["auth.api.key"]._retrieve_api_key(api_key)
            if auth_api_key:
                # reset _env on the request since we change the uid...
                # the next call to env will instantiate an new
                # odoo.api.Environment with the user defined on the
                # auth.api_key
                request._env = None
                request.update_env(user=auth_api_key.user_id.id)
                request.auth_api_key = api_key
                request.auth_api_key_id = auth_api_key.id
                return True
        _logger.error("Wrong HTTP_API_KEY, access denied")
        raise AccessDenied()
    
    @classmethod
    def _auth_method_jwt(cls):
        headers = request.httprequest.headers
        auth_header = headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            secret = request.env['ir.config_parameter'].sudo().get_param('jwt_secret_key')
            try:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if not user_id:
                    raise AccessDenied("Token tidak valid: user_id tidak ditemukan.")

                # Reset env dan inject user yang sesuai
                request._env = None
                request.update_env(user=user_id)
                request.jwt_payload = payload  # kalau butuh akses payload di controller

                blacklist = request.env["jwt.token.blacklist"].sudo()
                user_id = payload.get("user_id")
                jti = payload.get("jti")
                if jti:
                    if blacklist._is_blacklisted(jti):
                        raise AccessDenied()
                return True
            

            except jwt.ExpiredSignatureError:
                raise AccessDenied("Token telah kedaluwarsa.")
            except jwt.InvalidTokenError:
                raise AccessDenied("Token tidak valid.")
        
        raise AccessDenied("Authorization header bermasalah atau tidak ditemukan.")
