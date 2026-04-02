import hashlib
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class TracksolidConnector(models.AbstractModel):
    _name = 'tracksolid.connector'
    _description = 'Tracksolid API Connector'

    @api.model
    def _get_api_credentials(self):
        params = self.env['ir.config_parameter'].sudo()
        # Be EXTREMELY careful not to return None, ensuring string type for hashing logic
        base_url = (params.get_param('tracksolid.base_url') or '').strip()
        app_key = (params.get_param('tracksolid.app_key') or '').strip()
        app_secret = (params.get_param('tracksolid.app_secret') or '').strip()
        user_id = (params.get_param('tracksolid.user_id') or '').strip()
        password = (params.get_param('tracksolid.password') or '').strip()
        
        if not all([base_url, app_key, app_secret, user_id, password]):
            # Log what is missing for debugging (but mask secret)
            _logger.error(f"Tracksolid Config Missing: URL={bool(base_url)}, Key={bool(app_key)}, ID={bool(user_id)}")
            raise UserError(_("Tracksolid Credentials are not fully configured. Please check Settings."))
        
        return base_url, app_key, app_secret, user_id, password

    @api.model
    def _generate_signature(self, params, app_secret):
        # 1. Sort parameters by ASCII (alphabetical) of key
        sorted_keys = sorted(params.keys())
        
        # 2. Concatenate key + value
        # Note: Document usually says KeyValueKeyValue... need to be careful with types
        param_str = ""
        for key in sorted_keys:
            if key == 'sign':
                continue
            val = str(params[key])
            param_str += f"{key}{val}"
            
        # 3. Add AppSecret at head and tail
        raw_str = f"{app_secret}{param_str}{app_secret}"
        
        # 4. MD5 Hash and Uppercase
        signature = hashlib.md5(raw_str.encode('utf-8')).hexdigest().upper()
        return signature

    @api.model
    def _get_access_token(self):
        params_db = self.env['ir.config_parameter'].sudo()
        token = params_db.get_param('tracksolid.access_token')
        expiry = params_db.get_param('tracksolid.token_expiry')
        
        # Check if token is valid (give 5 min buffer)
        if token and expiry:
            expiry_dt = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < (expiry_dt - timedelta(minutes=5)):
                return token

        # If invalid, request new one
        base_url, app_key, app_secret, user_id, password = self._get_api_credentials()
        
        # Prepare parameters for token request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Based on docs (general guess for param names, adjust if needed from provided summary)
        # Summary says: app_key, user_id, user_pwd_md5, expires_in
        req_params = {
            'method': 'jimi.oauth.token.get',
            'timestamp': timestamp,
            'app_key': app_key,
            'v': '0.9',
            'format': 'json',
            'sign_method': 'md5',
            'user_id': user_id,
            'user_pwd_md5': password,
            'expires_in': 7200, # 2 hours
        }
        
        req_params['sign'] = self._generate_signature(req_params, app_secret)
        
        try:
            response = requests.post(base_url, data=req_params)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0 and result.get('result'):
                new_token = result['result']['accessToken']
                # Save token and expiry
                expiry_time = datetime.now() + timedelta(seconds=7200)
                params_db.set_param('tracksolid.access_token', new_token)
                params_db.set_param('tracksolid.token_expiry', expiry_time.strftime("%Y-%m-%d %H:%M:%S"))
                return new_token
            else:
                _logger.error(f"Tracksolid Auth Failed: {result}")
                raise UserError(f"Failed to authenticate with Tracksolid: {result.get('message', 'Unknown Error')}")
        except Exception as e:
            _logger.error(f"Tracksolid Connection Error: {str(e)}")
            raise UserError(f"Connection Error: {str(e)}")

    @api.model
    def _make_request(self, method, custom_params=None):
        base_url, app_key, app_secret, _, _ = self._get_api_credentials()
        token = self._get_access_token()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        api_params = {
            'method': method,
            'timestamp': timestamp,
            'app_key': app_key,
            'access_token': token,
            'v': '0.9',
            'format': 'json',
            'sign_method': 'md5',
        }
        
        if custom_params:
            api_params.update(custom_params)
            
        api_params['sign'] = self._generate_signature(api_params, app_secret)
        
        try:
            response = requests.post(base_url, data=api_params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('result')
            else:
                _logger.error(f"Tracksolid API Error ({method}): {data}")
                # If token expired invalid, maybe retry? For now, raise.
                if data.get('code') == 10003: # Example code for invalid token, hypothetically
                     # logic to clear token could go here
                     pass
                return None
        except Exception as e:
            _logger.error(f"Request Error ({method}): {str(e)}")
            return None
