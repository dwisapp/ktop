from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tracksolid_app_key = fields.Char(string="App Key", config_parameter='tracksolid.app_key')
    tracksolid_app_secret = fields.Char(string="App Secret", config_parameter='tracksolid.app_secret')
    tracksolid_user_id = fields.Char(string="User ID (Login)", config_parameter='tracksolid.user_id')
    tracksolid_target_user_id = fields.Char(string="Target Sub-Account ID", config_parameter='tracksolid.target_user_id',
                                            help="Leave empty to sync own devices. Fill with Child Account ID to sync their devices.")
    tracksolid_password = fields.Char(string="Password (MD5)", config_parameter='tracksolid.password', 
                                      help="The MD5 hash of your password")
    tracksolid_base_url = fields.Char(string="Base URL", config_parameter='tracksolid.base_url',
                                      default='http://open.10000track.com/route/rest')

    def action_sync_tracksolid(self):
        """ Manually trigger the sync of all vehicles """
        # Ensure values are saved before running the sync
        self.set_values()
        
        # Trigger sync
        try:
            self.env['fleet.vehicle'].sudo().cron_sync_all_vehicles()
        except UserError as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Connection Failed"),
                    'message': str(e),
                    'sticky': True,
                    'type': 'danger',
                }
            }
        except Exception as e:
             return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': str(e),
                    'sticky': True,
                    'type': 'danger',
                }
            }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sync Started"),
                'message': _("Vehicle synchronization successful! Data updated."),
                'sticky': False,
                'type': 'success',
            }
        }
