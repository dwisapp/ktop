# -*- coding: utf-8 -*-

from odoo import models, fields, api
import secrets


class ResUsers(models.Model):
    _inherit = 'res.users'

    api_key = fields.Char(
        string='API Key',
        help='API key for mobile app authentication',
        copy=False,
        readonly=True,
        index=True
    )

    def generate_api_key(self):
        """Generate new API key for user"""
        for user in self:
            user.api_key = secrets.token_urlsafe(32)
        return True

    def action_regenerate_api_key(self):
        """Regenerate API key (called from UI button)"""
        self.ensure_one()
        self.api_key = secrets.token_urlsafe(32)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'API Key Regenerated',
                'message': 'New API key has been generated successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
