from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    fleet_document_loan_approve_template = fields.Many2one('whatsapp.template', string='Fleet Document Loan Approve Template', related='company_id.fleet_document_loan_approve_template', readonly=False)
    fleet_document_loan_manager_template = fields.Many2one('whatsapp.template', string='Fleet Document Loan Manager Template', related='company_id.fleet_document_loan_manager_template', readonly=False)
    fleet_usage_location = fields.Many2one('stock.location', string='Fleet Usage Location', related='company_id.fleet_usage_location', readonly=False)