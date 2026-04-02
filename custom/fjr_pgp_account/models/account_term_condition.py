from odoo import models, fields, api, _

class AccountTermCondition(models.Model):
    _name = 'account.term.condition'
    _description = 'Account Term Condition'

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string='Description')