# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
import json
import logging
import base64

_logger = logging.getLogger(__name__)


class AttendanceAPI(http.Controller):
    """
    RESTful API for Mobile App / External System Integration

    Authentication: API Key or Session-based
    """

    # ==================== HELPER METHODS ====================

    def _authenticate_api_key(self, api_key):
        """
        Validate API key and return user

        Note: Implement your own API key validation
        For now, using simple token validation
        """
        if not api_key:
            return None

        # TODO: Implement proper API key validation
        # Example: Check against ir.config_parameter or custom model
        # For now, simple validation

        user = request.env['res.users'].sudo().search([
            ('api_key', '=', api_key)  # Assuming you add api_key field to res.users
        ], limit=1)

        return user if user else None

    def _json_response(self, data=None, error=None, status=200):
        """Generate JSON response"""
        response = request.make_response(
            json.dumps({
                'success': error is None,
                'data': data,
                'error': error
            }, default=str),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),  # CORS - adjust for production
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key'),
            ]
        )
        response.status_code = status
        return response

    # ==================== API ENDPOINTS ====================

    @http.route('/api/v1/attendance/check-in', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_check_in(self, **kwargs):
        """
        API Endpoint: Check-In with Photo + GPS

        Method: POST
        Authentication: API Key (Header: X-API-Key) or Session

        Body (JSON):
        {
            "photo": "base64_encoded_jpeg",
            "latitude": -6.028448,
            "longitude": 106.047287,
            "employee_id": 123  // optional if using API key
        }

        Response:
        {
            "success": true,
            "data": {
                "attendance_id": 456,
                "check_in": "2025-11-30 10:30:00",
                "employee_name": "John Doe",
                "gps_location": {
                    "latitude": -6.028448,
                    "longitude": 106.047287
                }
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            # Get API key from header
            api_key = request.httprequest.headers.get('X-API-Key')

            # Authenticate
            if request.session.uid:
                # Session-based auth (logged in user)
                user = request.env.user
            elif api_key:
                # API key auth
                user = self._authenticate_api_key(api_key)
                if not user:
                    return self._json_response(error='Invalid API key', status=401)
            else:
                return self._json_response(error='Authentication required', status=401)

            # Parse request body
            body = json.loads(request.httprequest.data.decode('utf-8'))

            photo_base64 = body.get('photo')
            latitude = body.get('latitude')
            longitude = body.get('longitude')
            employee_id = body.get('employee_id')

            # Validate required fields
            if not photo_base64:
                return self._json_response(error='Photo is required', status=400)

            # Get employee
            if employee_id:
                employee = request.env['hr.employee'].sudo().browse(employee_id)
            else:
                employee = user.employee_id

            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Check if already checked in
            if employee.attendance_state == 'checked_in':
                return self._json_response(error='Already checked in', status=400)

            # Create attendance record
            attendance = request.env['hr.attendance'].sudo().create({
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
                'check_in_image': photo_base64,
                'in_latitude': float(latitude) if latitude else False,
                'in_longitude': float(longitude) if longitude else False,
            })

            # Return success response
            return self._json_response(data={
                'attendance_id': attendance.id,
                'check_in': attendance.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                'employee_name': employee.name,
                'employee_id': employee.id,
                'gps_location': {
                    'latitude': attendance.in_latitude,
                    'longitude': attendance.in_longitude
                } if attendance.in_latitude else None
            })

        except Exception as e:
            _logger.exception("API check-in error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/attendance/check-out', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_check_out(self, **kwargs):
        """
        API Endpoint: Check-Out with Photo + GPS

        Method: POST
        Authentication: API Key (Header: X-API-Key) or Session

        Body (JSON):
        {
            "photo": "base64_encoded_jpeg",
            "latitude": -6.028448,
            "longitude": 106.047287,
            "employee_id": 123  // optional
        }

        Response:
        {
            "success": true,
            "data": {
                "attendance_id": 456,
                "check_out": "2025-11-30 18:30:00",
                "hours_worked": 8.0,
                "employee_name": "John Doe"
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            # Authenticate
            api_key = request.httprequest.headers.get('X-API-Key')

            if request.session.uid:
                user = request.env.user
            elif api_key:
                user = self._authenticate_api_key(api_key)
                if not user:
                    return self._json_response(error='Invalid API key', status=401)
            else:
                return self._json_response(error='Authentication required', status=401)

            # Parse request
            body = json.loads(request.httprequest.data.decode('utf-8'))

            photo_base64 = body.get('photo')
            latitude = body.get('latitude')
            longitude = body.get('longitude')
            employee_id = body.get('employee_id')

            # Validate
            if not photo_base64:
                return self._json_response(error='Photo is required', status=400)

            # Get employee
            if employee_id:
                employee = request.env['hr.employee'].sudo().browse(employee_id)
            else:
                employee = user.employee_id

            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Check if checked out
            if employee.attendance_state == 'checked_out':
                return self._json_response(error='Already checked out', status=400)

            # Find open attendance
            attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], limit=1)

            if not attendance:
                return self._json_response(error='No open attendance found', status=404)

            # Update with check-out
            attendance.sudo().write({
                'check_out': fields.Datetime.now(),
                'check_out_image': photo_base64,
                'out_latitude': float(latitude) if latitude else False,
                'out_longitude': float(longitude) if longitude else False,
            })

            # Return success
            return self._json_response(data={
                'attendance_id': attendance.id,
                'check_in': attendance.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                'check_out': attendance.check_out.strftime('%Y-%m-%d %H:%M:%S'),
                'hours_worked': round(attendance.worked_hours, 2),
                'employee_name': employee.name,
                'employee_id': employee.id,
            })

        except Exception as e:
            _logger.exception("API check-out error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/attendance/status', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_attendance_status(self, **kwargs):
        """
        API Endpoint: Get Employee Attendance Status

        Method: GET
        Authentication: API Key (Header: X-API-Key) or Session

        Query Params:
        - employee_id (optional)

        Response:
        {
            "success": true,
            "data": {
                "employee_id": 123,
                "employee_name": "John Doe",
                "status": "checked_in",  // or "checked_out"
                "last_attendance": {
                    "id": 456,
                    "check_in": "2025-11-30 10:30:00",
                    "check_out": null,
                    "hours_worked": 0
                }
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            # Authenticate
            api_key = request.httprequest.headers.get('X-API-Key')

            if request.session.uid:
                user = request.env.user
            elif api_key:
                user = self._authenticate_api_key(api_key)
                if not user:
                    return self._json_response(error='Invalid API key', status=401)
            else:
                return self._json_response(error='Authentication required', status=401)

            # Get employee
            employee_id = kwargs.get('employee_id')
            if employee_id:
                employee = request.env['hr.employee'].sudo().browse(int(employee_id))
            else:
                employee = user.employee_id

            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get last attendance
            last_attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id)
            ], order='check_in desc', limit=1)

            last_att_data = None
            if last_attendance:
                last_att_data = {
                    'id': last_attendance.id,
                    'check_in': last_attendance.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                    'check_out': last_attendance.check_out.strftime('%Y-%m-%d %H:%M:%S') if last_attendance.check_out else None,
                    'hours_worked': round(last_attendance.worked_hours, 2) if last_attendance.check_out else 0,
                    'has_check_in_photo': bool(last_attendance.check_in_image),
                    'has_check_out_photo': bool(last_attendance.check_out_image),
                }

            return self._json_response(data={
                'employee_id': employee.id,
                'employee_name': employee.name,
                'status': employee.attendance_state,  # 'checked_in' or 'checked_out'
                'last_attendance': last_att_data
            })

        except Exception as e:
            _logger.exception("API status error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/attendance/history', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_attendance_history(self, **kwargs):
        """
        API Endpoint: Get Attendance History

        Method: GET
        Authentication: API Key or Session

        Query Params:
        - employee_id (optional)
        - limit (default: 30)
        - date_from (format: YYYY-MM-DD)
        - date_to (format: YYYY-MM-DD)

        Response:
        {
            "success": true,
            "data": {
                "employee_id": 123,
                "employee_name": "John Doe",
                "attendances": [
                    {
                        "id": 456,
                        "check_in": "2025-11-30 10:30:00",
                        "check_out": "2025-11-30 18:30:00",
                        "hours_worked": 8.0,
                        "gps_check_in": {...},
                        "gps_check_out": {...}
                    }
                ]
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            # Authenticate
            api_key = request.httprequest.headers.get('X-API-Key')

            if request.session.uid:
                user = request.env.user
            elif api_key:
                user = self._authenticate_api_key(api_key)
                if not user:
                    return self._json_response(error='Invalid API key', status=401)
            else:
                return self._json_response(error='Authentication required', status=401)

            # Get parameters
            employee_id = kwargs.get('employee_id')
            limit = int(kwargs.get('limit', 30))
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')

            # Get employee
            if employee_id:
                employee = request.env['hr.employee'].sudo().browse(int(employee_id))
            else:
                employee = user.employee_id

            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Build domain
            domain = [('employee_id', '=', employee.id)]

            if date_from:
                domain.append(('check_in', '>=', date_from + ' 00:00:00'))
            if date_to:
                domain.append(('check_in', '<=', date_to + ' 23:59:59'))

            # Get attendances
            attendances = request.env['hr.attendance'].sudo().search(
                domain,
                order='check_in desc',
                limit=limit
            )

            # Format response
            att_list = []
            for att in attendances:
                att_list.append({
                    'id': att.id,
                    'check_in': att.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                    'check_out': att.check_out.strftime('%Y-%m-%d %H:%M:%S') if att.check_out else None,
                    'hours_worked': round(att.worked_hours, 2) if att.check_out else 0,
                    'gps_check_in': {
                        'latitude': att.in_latitude,
                        'longitude': att.in_longitude
                    } if att.in_latitude else None,
                    'gps_check_out': {
                        'latitude': att.out_latitude,
                        'longitude': att.out_longitude
                    } if att.out_latitude else None,
                    'has_check_in_photo': bool(att.check_in_image),
                    'has_check_out_photo': bool(att.check_out_image),
                })

            return self._json_response(data={
                'employee_id': employee.id,
                'employee_name': employee.name,
                'count': len(att_list),
                'attendances': att_list
            })

        except Exception as e:
            _logger.exception("API history error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/attendance/photo/<int:attendance_id>/<string:photo_type>', type='http', auth='public', methods=['GET'], csrf=False)
    def api_get_photo(self, attendance_id, photo_type, **kwargs):
        """
        API Endpoint: Get Photo Image

        Method: GET
        Authentication: API Key or Session

        URL: /api/v1/attendance/photo/{attendance_id}/{photo_type}
        - photo_type: "check_in" or "check_out"

        Response: JPEG image (binary)
        """
        try:
            # Authenticate
            api_key = request.httprequest.args.get('api_key') or request.httprequest.headers.get('X-API-Key')

            if not request.session.uid and not api_key:
                return request.make_response('Unauthorized', 401)

            # Get attendance
            attendance = request.env['hr.attendance'].sudo().browse(attendance_id)

            if not attendance.exists():
                return request.make_response('Not found', 404)

            # Get photo
            if photo_type == 'check_in':
                photo_data = attendance.check_in_image
            elif photo_type == 'check_out':
                photo_data = attendance.check_out_image
            else:
                return request.make_response('Invalid photo type', 400)

            if not photo_data:
                return request.make_response('Photo not found', 404)

            # Decode base64 and return image
            image_bytes = base64.b64decode(photo_data)

            return request.make_response(
                image_bytes,
                headers=[
                    ('Content-Type', 'image/jpeg'),
                    ('Content-Length', len(image_bytes)),
                ]
            )

        except Exception as e:
            _logger.exception("API get photo error")
            return request.make_response(str(e), 500)
