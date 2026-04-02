# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ===== SELFIE ATTENDANCE SETTINGS =====

    # Enable/Disable Features
    attendance_selfie_check_in = fields.Boolean(
        string='Require Selfie for Check-in',
        config_parameter='hr_attendance_selfie.check_in_required',
        default=True,
        help='Mandatory selfie photo saat check-in'
    )

    attendance_selfie_check_out = fields.Boolean(
        string='Require Selfie for Check-out',
        config_parameter='hr_attendance_selfie.check_out_required',
        default=True,
        help='Mandatory selfie photo saat check-out'
    )

    # Photo Quality Settings
    attendance_photo_quality = fields.Selection([
        ('low', 'Low (320x240 - ~50KB)'),
        ('medium', 'Medium (640x480 - ~150KB)'),
        ('high', 'High (1280x720 - ~400KB)'),
    ], string='Photo Quality',
        config_parameter='hr_attendance_selfie.photo_quality',
        default='medium',
        help='Kualitas photo yang di-capture'
    )

    attendance_photo_max_size = fields.Integer(
        string='Max Photo Size (KB)',
        config_parameter='hr_attendance_selfie.max_photo_size',
        default=500,
        help='Maximum file size dalam KB'
    )

    # Camera Settings
    attendance_camera_front_default = fields.Boolean(
        string='Use Front Camera by Default',
        config_parameter='hr_attendance_selfie.front_camera_default',
        default=True,
        help='Auto switch ke front camera untuk selfie (mobile devices)'
    )

    attendance_camera_show_preview = fields.Boolean(
        string='Show Camera Preview',
        config_parameter='hr_attendance_selfie.show_preview',
        default=True,
        help='Tampilkan live preview sebelum capture'
    )

    attendance_camera_allow_retake = fields.Boolean(
        string='Allow Retake Photo',
        config_parameter='hr_attendance_selfie.allow_retake',
        default=True,
        help='User bisa retake photo sebelum submit'
    )

    # GPS Settings
    attendance_use_gps = fields.Boolean(
        string='Capture GPS Location',
        config_parameter='hr_attendance_selfie.use_gps',
        default=True,
        help='Capture GPS location menggunakan Odoo built-in fields'
    )

    # Access Rights Settings
    attendance_employee_view_rights = fields.Selection([
        ('own', 'Own Photos Only'),
        ('department', 'Department Photos'),
        ('all', 'All Photos'),
    ], string='Employee Can View',
        config_parameter='hr_attendance_selfie.employee_view_rights',
        default='own',
        help='Photos yang bisa dilihat employee'
    )

    attendance_manager_view_rights = fields.Selection([
        ('department', 'Department Photos Only'),
        ('all', 'All Photos'),
    ], string='Manager Can View',
        config_parameter='hr_attendance_selfie.manager_view_rights',
        default='all',
        help='Photos yang bisa dilihat manager'
    )
