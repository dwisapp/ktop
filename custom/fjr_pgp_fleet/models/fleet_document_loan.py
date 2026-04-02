from odoo import models, fields, api, _
import uuid

class FleetDocumentLoan(models.Model):
    _name = 'fleet.document.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Document Loan for Fleet'



    name = fields.Char(string='Loan Number', required=True, copy=False,  index=True, default=lambda self: _('New'))
    
    # available_manager_ids = fields.Many2many('res.users', compute='_compute_available_manager_ids')
    manager_id = fields.Many2one('res.users', compute='_compute_from_employee_id', store=True, readonly=False,
                                 string='Manager', tracking=True)
    
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                   required=True, compute='_compute_employee_id', store=True, readonly=False,
                                   check_company=True,tracking=True,)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('in_loan', 'in Loan'),
        ('return', 'Return'),
        ('lost', 'Lost'),
        ('reject', 'Reject'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', copy=False, tracking=True)
    loan_purpose = fields.Text("Loan Purpose")
    date = fields.Date("Date", default=fields.Date.context_today, required=True)
    estimated_return_date = fields.Date("Estimated Return Date")
    fleet_id = fields.Many2one('fleet.vehicle', string='Fleet', required=True)
    document_id = fields.Many2one('fleet.document', string='Document', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    reject_reason = fields.Text("Reject Reason", tracking=True)
    return_date = fields.Date("Return Date")
    document_user_id = fields.Many2one("res.users", related="document_id.user_id", store=True)
    public_token = fields.Char('Public Token', copy=False)
    approval_link = fields.Char('Approval Link', copy=False)
    rejection_link = fields.Char('Rejection Link', copy=False)
    fleet_document_link = fields.Char('Document Link', compute='_compute_fleet_document_link')


    def _compute_fleet_document_link(self):
        for rec in self:
            # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            rec.fleet_document_link = f"/web#id={rec.id}&view_type=form&model=fleet.document.loan"


    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for loan in self:
                loan.employee_id = self.env.user.with_company(loan.company_id).employee_id


    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for sheet in self:
            sheet.manager_id = sheet.employee_id.parent_id.user_id

   
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.document.loan') or _('New')
        result = super(FleetDocumentLoan, self).create(vals)
        return result


    def action_request(self):
        self.document_id.write({'state': 'request'})
        self._generate_public_link()
        self._send_approval_whatsapp_message()
        self.write({'state': 'request'})
    
    def action_approve(self):
        self.document_id.write({'state': 'in_loan'})
        self.write({'state': 'in_loan',  'public_token' : False})


        

    def action_return(self):
        self.document_id.write({'state': 'available'})
        self.write({'state': 'return', 'return_date': fields.Date.context_today(self)})

    def action_lost(self):
        self.document_id.write({'state': 'lost'})
        self.write({'state': 'lost'})

    def action_reject(self):
        for doc in self.document_id.filtered(lambda doc: doc.state in ['request', 'in_loan']):
            doc.write({'state': 'available'})

        self._do_reject()

    def action_cancel(self):
        for doc in self.document_id.filtered(lambda doc: doc.state in ['request', 'in_loan']):
            doc.write({'state': 'available'})
        self.write({'state': 'cancel',  'public_token' : False}) 

    def action_draft(self):
        self.write({'state': 'draft'})


    def _do_reject(self, reject_reason=False):
        vals = {
            'state' : 'reject',
            'public_token' : False
        }
        if reject_reason:
            vals['reject_reason'] = reject_reason
        for rec in self:
            rec.write(vals)

    def _generate_public_link(self):
        for loan in self:
            public_token = uuid.uuid4().hex
            user_id = loan.document_user_id.id
            approval_url = '/fleet/document/loan/approve/%s/%s' % (public_token, user_id)
            rejection_url = '/fleet/document/loan/reject/%s/%s' % (public_token, user_id)
            loan.write({'public_token': public_token, 'approval_link': approval_url, 'rejection_link': rejection_url})

    def _send_approval_whatsapp_message(self):
        for loan in self:
            msg = _('Document Loan %s requested for approval by %s') % (loan.name, self.env.user.name)
            loan.message_post(body=msg)
            if not loan.approval_link:
                loan._generate_public_link()
            context = self._context
            document_user_context = dict(context)
            document_user_context.update({
                'active_model': 'fleet.document.loan',
                'active_id': loan.id,
                'no_partner_notification' : True
            })
            manager_context = document_user_context
            if loan.company_id.fleet_document_loan_approve_template:
                document_user_context.update({
                    'default_wa_template_id' : loan.company_id.fleet_document_loan_approve_template.id,})
                whatsapp_composer_user = self.env['whatsapp.composer'].with_context(document_user_context).create({
                    'res_model': 'fleet.document.loan',
                    'res_ids': str(loan.id),
                })
                whatsapp_composer_user._send_whatsapp_template()
            if loan.company_id.fleet_document_loan_manager_template and loan.manager_id:
                manager_context.update({
                    'default_wa_template_id' : loan.company_id.fleet_document_loan_manager_template.id,})
                whatsapp_composer_manager = self.env['whatsapp.composer'].with_context(manager_context).create({
                    'res_model': 'fleet.document.loan',
                    'res_ids': str(loan.id),
                })
                whatsapp_composer_manager._send_whatsapp_template()
            
