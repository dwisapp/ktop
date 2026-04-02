from odoo import models, fields, api, _
import requests
from odoo.exceptions import UserError
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jasa_erp_url = fields.Char('Jasa ERP URL', config_parameter='fjr_kasir_jasa_erp.jasa_erp_url')
    jasa_erp_email = fields.Char('Jasa ERP Email', config_parameter='fjr_kasir_jasa_erp.jasa_erp_email')
    jasa_erp_password = fields.Char('Jasa ERP Password', config_parameter='fjr_kasir_jasa_erp.jasa_erp_password')
    last_auth_date = fields.Datetime('Last Auth Date', config_parameter='fjr_kasir_jasa_erp.last_auth_date')
    last_get_data = fields.Datetime('Last Get Data', config_parameter='fjr_kasir_jasa_erp.last_get_data')
    jasa_erp_cookies = fields.Char('Jasa ERP Cookies', config_parameter='fjr_kasir_jasa_erp.jasa_erp_cookies')
    

    def auth_jasa_erp(self):
        url = self.jasa_erp_url
        email = self.jasa_erp_email
        password = self.jasa_erp_password
        response = requests.post(f"{url}/api/method/login?usr={email}&pwd={password}")
        if response.status_code == 200 or response.status_code == 201:
            self.env['ir.config_parameter'].set_param('fjr_kasir_jasa_erp.last_auth_date', fields.Datetime.now())
            cookies = response.cookies.get_dict()
            cookies_res = ""
            for key, value in cookies.items():
                cookies_res += f"{key}={value};"

            self.env['ir.config_parameter'].set_param('fjr_kasir_jasa_erp.jasa_erp_cookies', cookies_res)
                
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Successfully authenticated with Jasa ERP',
                    'type': 'rainbow_man',
                }

            }
        else:
            response_text = json.loads(response.text)
            message = response_text.get('message', '')

            

            raise UserError(_("Failed to authenticate with Jasa ERP, %s" % (message)))
            
       