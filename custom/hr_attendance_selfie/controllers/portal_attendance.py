# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import UserError
import logging
import base64

_logger = logging.getLogger(__name__)


class AttendancePortal(http.Controller):
    """
    Portal Controller for Employee Self-Service Attendance
    with Selfie Photo + GPS Tracking
    """

    @http.route('/my/attendance', type='http', auth='user', website=True)
    def attendance_portal_home(self, **kw):
        """
        Main attendance portal page
        Shows check-in/check-out interface with camera + GPS
        """
        employee = request.env.user.employee_id

        if not employee:
            return request.render('hr_attendance_selfie.portal_no_employee', {
                'page_name': 'attendance',
            })

        # Get current attendance state
        attendance_state = employee.attendance_state  # 'checked_in' or 'checked_out'

        # Get last attendance record
        last_attendance = request.env['hr.attendance'].search([
            ('employee_id', '=', employee.id)
        ], order='check_in desc', limit=1)

        # Get today's attendances
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        today_attendances = request.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', today_start)
        ], order='check_in desc')

        values = {
            'page_name': 'attendance',
            'employee': employee,
            'attendance_state': attendance_state,
            'last_attendance': last_attendance,
            'today_attendances': today_attendances,
        }

        return request.render('hr_attendance_selfie.portal_attendance_page', values)

    @http.route('/my/attendance/submit', type='json', auth='user', methods=['POST'])
    def attendance_submit(self, photo_base64=None, latitude=None, longitude=None, action='check_in'):
        """
        Submit attendance with photo and GPS

        Args:
            photo_base64: Base64 encoded photo (without data:image prefix)
            latitude: GPS latitude
            longitude: GPS longitude
            action: 'check_in' or 'check_out'

        Returns:
            dict: Success status and message
        """
        try:
            employee = request.env.user.employee_id

            if not employee:
                return {
                    'success': False,
                    'error': _('No employee record found for your user account.')
                }

            # Validate photo
            if not photo_base64:
                return {
                    'success': False,
                    'error': _('Selfie photo is required!')
                }

            # Validate GPS (optional but recommended)
            if not latitude or not longitude:
                _logger.warning(f"Attendance submitted without GPS for employee {employee.name}")

            # Process based on action
            if action == 'check_in':
                # Check if already checked in
                if employee.attendance_state == 'checked_in':
                    return {
                        'success': False,
                        'error': _('You are already checked in!')
                    }

                # Create new attendance record
                attendance = request.env['hr.attendance'].sudo().create({
                    'employee_id': employee.id,
                    'check_in': fields.Datetime.now(),
                    'check_in_image': photo_base64,
                    'in_latitude': float(latitude) if latitude else False,
                    'in_longitude': float(longitude) if longitude else False,
                })

                message = _('Check-in successful! Have a productive day!')

            elif action == 'check_out':
                # Check if already checked out
                if employee.attendance_state == 'checked_out':
                    return {
                        'success': False,
                        'error': _('You are already checked out!')
                    }

                # Find open attendance record
                attendance = request.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False)
                ], limit=1)

                if not attendance:
                    return {
                        'success': False,
                        'error': _('No open attendance record found. Please check-in first.')
                    }

                # Update with check-out data
                attendance.sudo().write({
                    'check_out': fields.Datetime.now(),
                    'check_out_image': photo_base64,
                    'out_latitude': float(latitude) if latitude else False,
                    'out_longitude': float(longitude) if longitude else False,
                })

                # Calculate worked hours
                worked_hours = attendance.worked_hours
                message = _('Check-out successful! You worked %.2f hours today.') % worked_hours

            else:
                return {
                    'success': False,
                    'error': _('Invalid action. Use "check_in" or "check_out".')
                }

            return {
                'success': True,
                'message': message,
                'attendance_id': attendance.id,
                'new_state': employee.attendance_state,
            }

        except Exception as e:
            _logger.exception("Error submitting attendance")
            return {
                'success': False,
                'error': _('An error occurred: %s') % str(e)
            }

    @http.route('/my/attendance/history', type='http', auth='user', website=True)
    def attendance_history(self, **kw):
        """
        Show attendance history for current employee
        """
        employee = request.env.user.employee_id

        if not employee:
            return request.render('hr_attendance_selfie.portal_no_employee', {
                'page_name': 'attendance',
            })

        # Get last 30 days attendance
        date_from = fields.Datetime.now() - fields.timedelta(days=30)
        attendances = request.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', date_from)
        ], order='check_in desc')

        values = {
            'page_name': 'attendance_history',
            'employee': employee,
            'attendances': attendances,
        }

        return request.render('hr_attendance_selfie.portal_attendance_history', values)
