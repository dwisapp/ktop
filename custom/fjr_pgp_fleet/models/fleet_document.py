from odoo import models, fields, api, _


class FleetDocument(models.Model):
    _name = 'fleet.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fleet Document'

    name = fields.Char(string='Name',compute='_compute_name', store=True)
    document_type = fields.Many2one('fleet.document.type', string='Document Type', required=True, ondelete='restrict')
    description = fields.Text(string='Description')
    document_attachment_ids = fields.Many2many('ir.attachment', string='Document Attachments')
    document_link = fields.Char(string='Document Link')
    fleet_id = fields.Many2one('fleet.vehicle', string='Fleet')
    state = fields.Selection([
        ('available', 'Available'),
        ('request', 'Request'),
        ('in_loan', 'In Loan'),
        ('lost', 'Lost'),
        ('destroyed', 'Destroyed'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),
    ], string='Status', default='available')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    
    @api.depends('document_type', 'fleet_id','description')
    def _compute_name(self):
        for rec in self:
            name = f'{rec.document_type.name} - {rec.fleet_id.name}'
            if rec.description:
                name += f' - {rec.description}'
            rec.name = name

    def action_set_to_lost(self):
        self.write({'state': 'lost'})

    def action_set_to_destroyed(self):
        self.write({'state': 'destroyed'})
    
    def action_set_to_sold(self):
        self.write({'state': 'sold'})

    def action_draft(self):
        self.write({'state': 'available'})
    
    def action_cancel(self):
        self.write({'state': 'cancel'})