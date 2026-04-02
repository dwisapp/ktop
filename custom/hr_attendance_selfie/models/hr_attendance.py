# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    # ===== SELFIE PHOTO FIELDS =====

    check_in_image = fields.Binary(
        string='Check-in Photo',
        attachment=True,
        help='Selfie photo saat check-in untuk validasi kehadiran'
    )

    check_in_image_small = fields.Binary(
        string='Check-in Photo (Thumbnail)',
        compute='_compute_image_thumbnails',
        store=True,
        attachment=True,
        help='Thumbnail untuk display di list view'
    )

    check_out_image = fields.Binary(
        string='Check-out Photo',
        attachment=True,
        help='Selfie photo saat check-out'
    )

    check_out_image_small = fields.Binary(
        string='Check-out Photo (Thumbnail)',
        compute='_compute_image_thumbnails',
        store=True,
        attachment=True,
        help='Thumbnail untuk display di list view'
    )

    # ===== COMPUTED FIELDS =====

    @api.depends('check_in_image', 'check_out_image')
    def _compute_image_thumbnails(self):
        """Generate thumbnails untuk list view (150x150)"""
        for record in self:
            if record.check_in_image:
                record.check_in_image_small = self._resize_image(record.check_in_image, size=(150, 150))
            else:
                record.check_in_image_small = False

            if record.check_out_image:
                record.check_out_image_small = self._resize_image(record.check_out_image, size=(150, 150))
            else:
                record.check_out_image_small = False

    def _resize_image(self, image_data, size=(150, 150)):
        """Helper untuk resize image"""
        try:
            from PIL import Image
            import io

            if not image_data:
                return False

            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            image.thumbnail(size, Image.Resampling.LANCZOS)

            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            return base64.b64encode(output.getvalue())
        except Exception:
            # Fallback jika PIL tidak available atau error
            return image_data

    # ===== CONSTRAINTS & VALIDATIONS =====

    @api.constrains('check_in_image')
    def _check_check_in_image_required(self):
        """Validasi: Check-in photo WAJIB"""
        for record in self:
            # Skip validation untuk manual mode
            if record.in_mode == 'manual':
                continue

            # Check-in photo wajib
            if record.check_in and not record.check_in_image:
                raise ValidationError(_(
                    'Check-in photo is required!\n\n'
                    'Please ensure:\n'
                    '• Camera permission is allowed in your browser\n'
                    '• Camera is working properly\n'
                    '• You captured a selfie photo before check-in\n\n'
                    'If the problem persists, try refreshing the page or contact IT support.'
                ))

    @api.constrains('check_out_image')
    def _check_check_out_image_required(self):
        """Validasi: Check-out photo WAJIB"""
        for record in self:
            # Skip validation untuk manual mode
            if record.out_mode == 'manual':
                continue

            # Check-out photo wajib
            if record.check_out and not record.check_out_image:
                raise ValidationError(_(
                    'Check-out photo is required!\n\n'
                    'Please ensure:\n'
                    '• Camera permission is allowed in your browser\n'
                    '• Camera is working properly\n'
                    '• You captured a selfie photo before check-out\n\n'
                    'If the problem persists, try refreshing the page or contact IT support.'
                ))

    # ===== CRUD OVERRIDES =====

    @api.model
    def create(self, vals):
        """Enforce photo requirement saat create"""

        # Skip validation untuk manual mode
        if vals.get('in_mode') != 'manual':
            if 'check_in' in vals and vals.get('check_in'):
                if not vals.get('check_in_image'):
                    raise UserError(_(
                        'Check-in photo is mandatory!\n\n'
                        'Please capture a selfie photo before checking in.\n'
                        'Make sure camera permission is allowed in your browser.'
                    ))

        return super(HrAttendance, self).create(vals)

    def write(self, vals):
        """Enforce photo requirement saat write (check-out)"""

        # Check untuk setiap record
        for record in self:
            # Skip validation untuk manual mode
            if record.out_mode == 'manual' or vals.get('out_mode') == 'manual':
                continue

            # Jika ada check-out, photo wajib
            if 'check_out' in vals and vals.get('check_out'):
                if not vals.get('check_out_image'):
                    raise UserError(_(
                        'Check-out photo is mandatory!\n\n'
                        'Please capture a selfie photo before checking out.\n'
                        'Make sure camera permission is allowed in your browser.'
                    ))

        return super(HrAttendance, self).write(vals)

    # ===== BUSINESS METHODS =====

    def action_view_check_in_photo(self):
        """View check-in photo fullscreen"""
        self.ensure_one()

        if not self.check_in_image:
            raise UserError(_('No check-in photo available for this attendance record.'))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/image?model=hr.attendance&id={self.id}&field=check_in_image',
            'target': 'new',
        }

    def action_view_check_out_photo(self):
        """View check-out photo fullscreen"""
        self.ensure_one()

        if not self.check_out_image:
            raise UserError(_('No check-out photo available for this attendance record.'))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/image?model=hr.attendance&id={self.id}&field=check_out_image',
            'target': 'new',
        }
