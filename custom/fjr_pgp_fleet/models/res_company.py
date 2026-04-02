from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    fleet_document_loan_approve_template = fields.Many2one('whatsapp.template', string='Fleet Document Loan Approve Template')
    fleet_document_loan_manager_template = fields.Many2one('whatsapp.template', string='Fleet Document Loan Manager Template')
    fleet_usage_location = fields.Many2one('stock.location', string='Fleet Usage Location')