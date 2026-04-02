# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Selfie",

    'summary': """
        Selfie photo validation for employee check-in and check-out with GPS tracking
    """,

    'description': """
        HR Attendance Selfie Validation
        ================================

        Features:
        ---------
        * 📸 **Mandatory Selfie Photo** for check-in and check-out
        * 📍 **GPS Location Tracking** using Odoo built-in fields
        * 🖼️ **Photo Thumbnails** in attendance list view
        * 📱 **Mobile & Desktop Support** - works on webcam and phone camera
        * ⚙️ **Configurable Settings** - photo quality, resolution, camera preferences
        * 🔒 **Access Rights** - employees see own photos, managers see all
        * 🎯 **One-Click Flow** - popup modal with live camera preview

        How It Works:
        -------------
        1. Employee clicks "Check In"
        2. Camera popup appears with live preview
        3. GPS location auto-detected (Odoo built-in)
        4. Employee captures selfie photo
        5. Photo & GPS submitted together
        6. Same flow for Check Out

        Technical:
        ----------
        * Uses browser MediaDevices API for camera access
        * Stores photos as binary attachments (efficient)
        * Leverages Odoo 17 built-in GPS fields (in_latitude, in_longitude)
        * Responsive design for mobile and desktop
        * Works on HTTPS or localhost

        Requirements:
        -------------
        * Browser must support camera access (MediaDevices API)
        * User must allow camera permission
        * Works on HTTPS or localhost
        * Odoo 17 Community/Enterprise
    """,

    'author': "PTP GP Development Team",
    'website': "https://www.ptpgp.com",
    'category': 'Human Resources/Attendances',
    'version': '17.0.1.0.0',

    # Dependencies
    'depends': [
        'hr_attendance',
        'portal',
    ],

    # Data files
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/res_config_settings_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_announcement_views.xml',
        # Portal Templates
        'views/portal_templates.xml',
    ],

    # Assets
    'assets': {
        'web.assets_backend': [
            'hr_attendance_selfie/static/src/js/attendance_camera_widget.js',
            'hr_attendance_selfie/static/src/css/attendance_camera.css',
            'hr_attendance_selfie/static/src/xml/camera_templates.xml',
        ],
        'web.assets_frontend': [
            # Portal attendance page (employee self-service)
            'hr_attendance_selfie/static/src/js/portal_attendance.js',
            'hr_attendance_selfie/static/src/css/portal_attendance.css',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
