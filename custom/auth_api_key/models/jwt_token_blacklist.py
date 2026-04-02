from odoo import models, fields, api, _
from odoo import tools

class JwtTokenBlacklist(models.Model):
    _name = "jwt.token.blacklist"
    _description = "JWT Token Blacklist"

    jti = fields.Char(string="JWT ID", required=True, index=True)
    user_id = fields.Many2one('res.users', string="User", index=True)
    expired_at = fields.Datetime(string="Expired At", required=True, index=True)

    @api.model
    @tools.ormcache("jti")
    def _is_blacklisted(self, jti):
        record = self.search([
            ("jti", "=", jti),
            ("expired_at", ">", fields.Datetime.now())
        ], limit=1)
        return bool(record)
    

    def _clear_key_cache(self):
        self.env.registry.clear_cache()

    @api.model
    def create(self, vals):
        res = super(JwtTokenBlacklist, self).create(vals)
        self._clear_key_cache()
        return res