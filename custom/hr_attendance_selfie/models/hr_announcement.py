# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrAnnouncement(models.Model):
    _name = 'hr.announcement'
    _description = 'HR Announcement'
    _order = 'priority desc, date_from desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(
        string='Active',
        default=True
    )
    name = fields.Char(
        string='Title',
        required=True,
        tracking=True
    )
    description = fields.Html(
        string='Description',
        required=True
    )
    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    date_to = fields.Date(
        string='End Date',
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True)

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    department_ids = fields.Many2many(
        'hr.department',
        string='Target Departments',
        help='Leave empty to show to all departments'
    )

    employee_ids = fields.Many2many(
        'hr.employee',
        string='Target Employees',
        help='Leave empty to show to all employees'
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments'
    )

    is_pinned = fields.Boolean(
        string='Pinned',
        help='Pinned announcements appear at the top',
        default=False
    )

    def action_publish(self):
        """Publish announcement"""
        self.write({'state': 'published'})

    def action_archive(self):
        """Archive announcement"""
        self.write({'state': 'archived'})

    def action_draft(self):
        """Set to draft"""
        self.write({'state': 'draft'})

    @api.model
    def get_active_announcements_for_employee(self, employee_id):
        """Get active announcements for specific employee"""
        today = fields.Date.today()

        domain = [
            ('state', '=', 'published'),
            '|', ('date_to', '=', False), ('date_to', '>=', today),
            ('date_from', '<=', today),
        ]

        # Get employee
        employee = self.env['hr.employee'].browse(employee_id)

        if not employee.exists():
            return self.browse()

        # Filter by department or employee
        announcements = self.search(domain)

        # Filter announcements that target this employee
        result = self.browse()
        for announcement in announcements:
            # If no specific targets, show to everyone
            if not announcement.department_ids and not announcement.employee_ids:
                result |= announcement
            # If employee is in target employees
            elif employee in announcement.employee_ids:
                result |= announcement
            # If employee's department is in target departments
            elif employee.department_id and employee.department_id in announcement.department_ids:
                result |= announcement

        return result
