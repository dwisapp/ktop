# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
import json
import logging
import base64
import secrets
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class EmployeeAPI(http.Controller):
    """
    Complete Employee API for Mobile App

    Features:
    - Login/Authentication
    - Payslip (Slip Gaji)
    - Leave/Time Off (Cuti)
    - Employee Profile
    """

    # ==================== HELPER METHODS ====================

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
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key'),
            ]
        )
        response.status_code = status
        return response

    def _authenticate(self):
        """Authenticate user via session or API key"""
        api_key = request.httprequest.headers.get('X-API-Key')

        if request.session.uid:
            return request.env.user
        elif api_key:
            # Simple API key validation - customize as needed
            user = request.env['res.users'].sudo().search([
                ('login', '!=', False),  # Any valid user for now
            ], limit=1)
            # TODO: Implement proper API key validation
            return user if api_key else None
        return None

    # ==================== AUTHENTICATION API ====================

    @http.route('/api/v1/auth/login', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_login(self, **kwargs):
        """
        Login API - Authenticate employee

        POST /api/v1/auth/login
        Body: {
            "username": "employee@company.com",
            "password": "password123"
        }

        Response: {
            "success": true,
            "data": {
                "user_id": 123,
                "username": "employee@company.com",
                "name": "John Doe",
                "employee_id": 456,
                "employee_name": "John Doe",
                "api_key": "generated_token_here",
                "session_id": "session_token"
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
            username = body.get('username')
            password = body.get('password')

            if not username or not password:
                return self._json_response(error='Username and password required', status=400)

            # Authenticate
            db = request.session.db or request.db
            uid = request.session.authenticate(db, username, password)

            if not uid:
                return self._json_response(error='Invalid username or password', status=401)

            # Get user and employee info
            user = request.env['res.users'].sudo().browse(uid)
            employee = user.employee_id

            if not employee:
                return self._json_response(error='User is not linked to an employee', status=404)

            # Generate and store API key
            if not user.api_key:
                user.sudo().write({'api_key': secrets.token_urlsafe(32)})

            api_key = user.api_key

            return self._json_response(data={
                'user_id': user.id,
                'username': user.login,
                'name': user.name,
                'email': user.email or user.login,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'employee_code': employee.barcode or '',
                'department': employee.department_id.name if employee.department_id else None,
                'job_title': employee.job_id.name if employee.job_id else None,
                'api_key': api_key,
                'session_id': request.session.sid,
            })

        except Exception as e:
            _logger.exception("Login error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/auth/logout', type='http', auth='user', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_logout(self, **kwargs):
        """
        Logout API

        POST /api/v1/auth/logout
        Headers: X-API-Key or Session

        Response: {
            "success": true,
            "data": {"message": "Logged out successfully"}
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            request.session.logout()
            return self._json_response(data={'message': 'Logged out successfully'})
        except Exception as e:
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/auth/me', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_get_profile(self, **kwargs):
        """
        Get Current User Profile

        GET /api/v1/auth/me
        Headers: X-API-Key

        Response: {
            "success": true,
            "data": {
                "user_id": 123,
                "employee_id": 456,
                "name": "John Doe",
                "email": "john@company.com",
                "phone": "+62812345678",
                "department": "IT Department",
                "job_title": "Software Engineer",
                "manager": "Jane Smith",
                "work_email": "john@company.com",
                "work_phone": "+62812345678"
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            return self._json_response(data={
                'user_id': user.id,
                'employee_id': employee.id,
                'name': employee.name,
                'email': user.email or user.login,
                'phone': employee.mobile_phone or employee.work_phone or '',
                'department': employee.department_id.name if employee.department_id else None,
                'job_title': employee.job_id.name if employee.job_id else None,
                'manager': employee.parent_id.name if employee.parent_id else None,
                'work_email': employee.work_email or '',
                'work_phone': employee.work_phone or '',
                'employee_code': employee.barcode or '',
                'company': employee.company_id.name if employee.company_id else None,
            })

        except Exception as e:
            _logger.exception("Get profile error")
            return self._json_response(error=str(e), status=500)

    # ==================== PAYSLIP API ====================

    @http.route('/api/v1/payslip/list', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_payslip_list(self, **kwargs):
        """
        Get Payslip List

        GET /api/v1/payslip/list
        Query params:
        - year (optional): 2025
        - month (optional): 1-12
        - state (optional): draft, done, paid
        - limit (optional, default: 12)

        Response: {
            "success": true,
            "data": {
                "count": 12,
                "payslips": [
                    {
                        "id": 789,
                        "name": "Salary Slip - November 2025",
                        "date_from": "2025-11-01",
                        "date_to": "2025-11-30",
                        "state": "done",
                        "net_wage": 10000000.0,
                        "company_id": 1,
                        "struct_id": "Regular Pay"
                    }
                ]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get parameters
            year = kwargs.get('year')
            month = kwargs.get('month')
            state = kwargs.get('state')
            limit = int(kwargs.get('limit', 12))

            # Build domain
            domain = [('employee_id', '=', employee.id)]

            if year and month:
                date_from = f"{year}-{int(month):02d}-01"
                domain.append(('date_from', '>=', date_from))
                # Calculate last day of month
                if int(month) == 12:
                    date_to = f"{int(year)+1}-01-01"
                else:
                    date_to = f"{year}-{int(month)+1:02d}-01"
                domain.append(('date_from', '<', date_to))
            elif year:
                domain.append(('date_from', '>=', f"{year}-01-01"))
                domain.append(('date_from', '<', f"{int(year)+1}-01-01"))

            if state:
                domain.append(('state', '=', state))

            # Get payslips
            payslips = request.env['hr.payslip'].sudo().search(
                domain,
                order='date_from desc',
                limit=limit
            )

            # Format response
            payslip_list = []
            for slip in payslips:
                payslip_list.append({
                    'id': slip.id,
                    'name': slip.name,
                    'number': slip.number or '',
                    'date_from': slip.date_from.strftime('%Y-%m-%d'),
                    'date_to': slip.date_to.strftime('%Y-%m-%d'),
                    'state': slip.state,
                    'state_display': dict(slip._fields['state'].selection).get(slip.state),
                    'basic_wage': float(slip.basic_wage or 0),
                    'net_wage': float(slip.net_wage or 0),
                    'company_id': slip.company_id.id,
                    'company_name': slip.company_id.name,
                    'struct_id': slip.struct_id.name if slip.struct_id else '',
                })

            return self._json_response(data={
                'count': len(payslip_list),
                'payslips': payslip_list
            })

        except Exception as e:
            _logger.exception("Payslip list error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/payslip/<int:payslip_id>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_payslip_detail(self, payslip_id, **kwargs):
        """
        Get Payslip Detail

        GET /api/v1/payslip/{payslip_id}

        Response: {
            "success": true,
            "data": {
                "id": 789,
                "name": "Salary Slip - November 2025",
                "number": "SLIP/2025/11/001",
                "date_from": "2025-11-01",
                "date_to": "2025-11-30",
                "state": "done",
                "employee_name": "John Doe",
                "basic_wage": 8000000.0,
                "net_wage": 10000000.0,
                "lines": [
                    {
                        "name": "Basic Salary",
                        "code": "BASIC",
                        "category": "Allowance",
                        "amount": 8000000.0
                    },
                    {
                        "name": "Transport Allowance",
                        "code": "TRANS",
                        "category": "Allowance",
                        "amount": 500000.0
                    }
                ]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get payslip
            payslip = request.env['hr.payslip'].sudo().browse(payslip_id)

            if not payslip.exists():
                return self._json_response(error='Payslip not found', status=404)

            # Check if payslip belongs to employee
            if payslip.employee_id.id != employee.id:
                return self._json_response(error='Access denied', status=403)

            # Get payslip lines
            lines = []
            for line in payslip.line_ids:
                lines.append({
                    'id': line.id,
                    'name': line.name,
                    'code': line.code,
                    'category': line.category_id.name if line.category_id else '',
                    'sequence': line.sequence,
                    'quantity': float(line.quantity),
                    'rate': float(line.rate),
                    'amount': float(line.amount),
                    'total': float(line.total),
                })

            return self._json_response(data={
                'id': payslip.id,
                'name': payslip.name,
                'number': payslip.number or '',
                'date_from': payslip.date_from.strftime('%Y-%m-%d'),
                'date_to': payslip.date_to.strftime('%Y-%m-%d'),
                'date_payment': payslip.date.strftime('%Y-%m-%d') if payslip.date else None,
                'state': payslip.state,
                'state_display': dict(payslip._fields['state'].selection).get(payslip.state),
                'employee_id': payslip.employee_id.id,
                'employee_name': payslip.employee_id.name,
                'employee_code': payslip.employee_id.barcode or '',
                'contract': payslip.contract_id.name if payslip.contract_id else '',
                'struct': payslip.struct_id.name if payslip.struct_id else '',
                'basic_wage': float(payslip.basic_wage or 0),
                'net_wage': float(payslip.net_wage or 0),
                'company': payslip.company_id.name,
                'lines': lines,
                'note': payslip.note or '',
            })

        except Exception as e:
            _logger.exception("Payslip detail error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/payslip/<int:payslip_id>/download', type='http', auth='public', methods=['GET'], csrf=False)
    def api_payslip_download(self, payslip_id, **kwargs):
        """
        Download Payslip PDF

        GET /api/v1/payslip/{payslip_id}/download

        Response: PDF file (binary)
        """
        try:
            user = self._authenticate()
            if not user:
                return request.make_response('Unauthorized', 401)

            employee = user.employee_id
            if not employee:
                return request.make_response('No employee record', 404)

            # Get payslip
            payslip = request.env['hr.payslip'].sudo().browse(payslip_id)

            if not payslip.exists():
                return request.make_response('Not found', 404)

            # Check access
            if payslip.employee_id.id != employee.id:
                return request.make_response('Access denied', 403)

            # Generate PDF
            pdf_content, content_type = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'hr_payroll.action_report_payslip',
                [payslip.id]
            )

            # Return PDF
            return request.make_response(
                pdf_content,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="payslip_{payslip.number or payslip.id}.pdf"'),
                    ('Content-Length', len(pdf_content)),
                ]
            )

        except Exception as e:
            _logger.exception("Payslip download error")
            return request.make_response(str(e), 500)

    # ==================== LEAVE / TIME OFF API ====================

    @http.route('/api/v1/leave/balance', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_leave_balance(self, **kwargs):
        """
        Get Leave Balance

        GET /api/v1/leave/balance

        Response: {
            "success": true,
            "data": {
                "employee_id": 456,
                "employee_name": "John Doe",
                "balances": [
                    {
                        "leave_type_id": 1,
                        "leave_type": "Annual Leave",
                        "remaining": 12.0,
                        "taken": 3.0,
                        "total": 15.0
                    }
                ]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get leave types
            leave_types = request.env['hr.leave.type'].sudo().search([])

            balances = []
            for leave_type in leave_types:
                # Get allocation for this leave type
                allocation = request.env['hr.leave.allocation'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('holiday_status_id', '=', leave_type.id),
                    ('state', '=', 'validate')
                ], limit=1)

                if allocation:
                    # Get remaining leaves
                    remaining = employee.sudo()._get_leave_days_data(
                        fields.Date.today(),
                        employee_ids=[employee.id],
                        leave_type_ids=[leave_type.id]
                    ).get(employee.id, {}).get(leave_type.id, {})

                    balances.append({
                        'leave_type_id': leave_type.id,
                        'leave_type': leave_type.name,
                        'remaining': float(remaining.get('remaining_leaves', 0)),
                        'virtual_remaining': float(remaining.get('virtual_remaining_leaves', 0)),
                        'max_leaves': float(remaining.get('max_leaves', 0)),
                        'leaves_taken': float(remaining.get('leaves_taken', 0)),
                    })

            return self._json_response(data={
                'employee_id': employee.id,
                'employee_name': employee.name,
                'balances': balances
            })

        except Exception as e:
            _logger.exception("Leave balance error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/leave/list', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_leave_list(self, **kwargs):
        """
        Get Leave Requests List

        GET /api/v1/leave/list
        Query params:
        - state: draft, confirm, validate, refuse
        - date_from: YYYY-MM-DD
        - date_to: YYYY-MM-DD
        - limit: default 50

        Response: {
            "success": true,
            "data": {
                "count": 5,
                "leaves": [...]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get parameters
            state = kwargs.get('state')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            limit = int(kwargs.get('limit', 50))

            # Build domain
            domain = [('employee_id', '=', employee.id)]

            if state:
                domain.append(('state', '=', state))
            if date_from:
                domain.append(('request_date_from', '>=', date_from))
            if date_to:
                domain.append(('request_date_to', '<=', date_to))

            # Get leaves
            leaves = request.env['hr.leave'].sudo().search(
                domain,
                order='request_date_from desc',
                limit=limit
            )

            # Format response
            leave_list = []
            for leave in leaves:
                leave_list.append({
                    'id': leave.id,
                    'name': leave.name or leave.holiday_status_id.name,
                    'leave_type': leave.holiday_status_id.name,
                    'leave_type_id': leave.holiday_status_id.id,
                    'date_from': leave.request_date_from.strftime('%Y-%m-%d'),
                    'date_to': leave.request_date_to.strftime('%Y-%m-%d'),
                    'number_of_days': float(leave.number_of_days),
                    'state': leave.state,
                    'state_display': dict(leave._fields['state'].selection).get(leave.state),
                    'request_date': leave.create_date.strftime('%Y-%m-%d %H:%M:%S') if leave.create_date else None,
                })

            return self._json_response(data={
                'count': len(leave_list),
                'leaves': leave_list
            })

        except Exception as e:
            _logger.exception("Leave list error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/leave/request', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_leave_request(self, **kwargs):
        """
        Request Leave / Time Off

        POST /api/v1/leave/request
        Body: {
            "leave_type_id": 1,
            "date_from": "2025-12-01",
            "date_to": "2025-12-05",
            "description": "Family vacation"
        }

        Response: {
            "success": true,
            "data": {
                "leave_id": 999,
                "message": "Leave request submitted successfully"
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Parse request
            body = json.loads(request.httprequest.data.decode('utf-8'))

            leave_type_id = body.get('leave_type_id')
            date_from = body.get('date_from')
            date_to = body.get('date_to')
            description = body.get('description', '')

            # Validate
            if not leave_type_id or not date_from or not date_to:
                return self._json_response(error='leave_type_id, date_from, and date_to are required', status=400)

            # Create leave request
            leave = request.env['hr.leave'].sudo().create({
                'employee_id': employee.id,
                'holiday_status_id': leave_type_id,
                'request_date_from': date_from,
                'request_date_to': date_to,
                'name': description or 'Leave Request',
            })

            return self._json_response(data={
                'leave_id': leave.id,
                'message': 'Leave request submitted successfully',
                'state': leave.state,
                'number_of_days': float(leave.number_of_days),
            })

        except Exception as e:
            _logger.exception("Leave request error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/leave/<int:leave_id>/cancel', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_leave_cancel(self, leave_id, **kwargs):
        """
        Cancel Leave Request

        POST /api/v1/leave/{leave_id}/cancel

        Response: {
            "success": true,
            "data": {"message": "Leave cancelled successfully"}
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get leave
            leave = request.env['hr.leave'].sudo().browse(leave_id)

            if not leave.exists():
                return self._json_response(error='Leave not found', status=404)

            # Check if belongs to employee
            if leave.employee_id.id != employee.id:
                return self._json_response(error='Access denied', status=403)

            # Cancel leave
            if leave.state not in ['draft', 'confirm']:
                return self._json_response(error='Leave cannot be cancelled in current state', status=400)

            leave.action_refuse()

            return self._json_response(data={
                'message': 'Leave cancelled successfully'
            })

        except Exception as e:
            _logger.exception("Leave cancel error")
            return self._json_response(error=str(e), status=500)

    # ==================== ANNOUNCEMENT API ====================

    @http.route('/api/v1/announcement/list', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_announcement_list(self, **kwargs):
        """
        Get Announcement List

        GET /api/v1/announcement/list
        Query params:
        - limit (optional, default: 50)
        - state (optional): draft, published, archived
        - pinned_only (optional): true/false

        Response: {
            "success": true,
            "data": {
                "count": 5,
                "announcements": [
                    {
                        "id": 1,
                        "title": "Holiday Notice",
                        "description": "Office will be closed...",
                        "date_from": "2025-12-01",
                        "date_to": "2025-12-05",
                        "priority": "2",
                        "is_pinned": true,
                        "state": "published"
                    }
                ]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get parameters
            limit = int(kwargs.get('limit', 50))
            state = kwargs.get('state')
            pinned_only = kwargs.get('pinned_only', '').lower() == 'true'

            # Get active announcements for this employee
            announcements = request.env['hr.announcement'].sudo().get_active_announcements_for_employee(employee.id)

            # Additional filters
            if state:
                announcements = announcements.filtered(lambda a: a.state == state)
            if pinned_only:
                announcements = announcements.filtered(lambda a: a.is_pinned)

            # Limit
            announcements = announcements[:limit]

            # Format response
            announcement_list = []
            for announcement in announcements:
                announcement_list.append({
                    'id': announcement.id,
                    'title': announcement.name,
                    'description': announcement.description or '',
                    'date_from': announcement.date_from.strftime('%Y-%m-%d') if announcement.date_from else None,
                    'date_to': announcement.date_to.strftime('%Y-%m-%d') if announcement.date_to else None,
                    'priority': announcement.priority,
                    'priority_display': dict(announcement._fields['priority'].selection).get(announcement.priority),
                    'is_pinned': announcement.is_pinned,
                    'state': announcement.state,
                    'company': announcement.company_id.name if announcement.company_id else None,
                })

            return self._json_response(data={
                'count': len(announcement_list),
                'announcements': announcement_list
            })

        except Exception as e:
            _logger.exception("Announcement list error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/announcement/<int:announcement_id>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_announcement_detail(self, announcement_id, **kwargs):
        """
        Get Announcement Detail

        GET /api/v1/announcement/{announcement_id}

        Response: {
            "success": true,
            "data": {
                "id": 1,
                "title": "Holiday Notice",
                "description": "Office will be closed...",
                "date_from": "2025-12-01",
                "date_to": "2025-12-05",
                "priority": "2",
                "is_pinned": true,
                "state": "published",
                "attachments": [...]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get announcement
            announcement = request.env['hr.announcement'].sudo().browse(announcement_id)

            if not announcement.exists():
                return self._json_response(error='Announcement not found', status=404)

            # Check if employee can access this announcement
            active_announcements = request.env['hr.announcement'].sudo().get_active_announcements_for_employee(employee.id)
            if announcement not in active_announcements and announcement.state == 'published':
                # Allow access if published, even if not specifically targeted
                pass
            elif announcement.state != 'published':
                return self._json_response(error='Announcement not available', status=403)

            # Format attachments
            attachments = []
            for att in announcement.attachment_ids:
                attachments.append({
                    'id': att.id,
                    'name': att.name,
                    'mimetype': att.mimetype,
                    'file_size': att.file_size,
                    'url': f'/web/content/{att.id}?download=true',
                })

            return self._json_response(data={
                'id': announcement.id,
                'title': announcement.name,
                'description': announcement.description or '',
                'date_from': announcement.date_from.strftime('%Y-%m-%d') if announcement.date_from else None,
                'date_to': announcement.date_to.strftime('%Y-%m-%d') if announcement.date_to else None,
                'priority': announcement.priority,
                'priority_display': dict(announcement._fields['priority'].selection).get(announcement.priority),
                'is_pinned': announcement.is_pinned,
                'state': announcement.state,
                'company': announcement.company_id.name if announcement.company_id else None,
                'attachments': attachments,
            })

        except Exception as e:
            _logger.exception("Announcement detail error")
            return self._json_response(error=str(e), status=500)

    # ==================== APPROVAL API ====================

    @http.route('/api/v1/approval/list', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def api_approval_list(self, **kwargs):
        """
        Get List of Items Pending Approval

        GET /api/v1/approval/list
        Query params:
        - type (optional): leave, expense, all (default: all)
        - limit (optional, default: 50)

        Response: {
            "success": true,
            "data": {
                "count": 3,
                "approvals": [
                    {
                        "id": 123,
                        "type": "leave",
                        "title": "Annual Leave - John Doe",
                        "employee_name": "John Doe",
                        "date_from": "2025-12-01",
                        "date_to": "2025-12-05",
                        "days": 5,
                        "state": "confirm",
                        "request_date": "2025-11-28"
                    }
                ]
            }
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Get parameters
            approval_type = kwargs.get('type', 'all')
            limit = int(kwargs.get('limit', 50))

            approvals = []

            # Get Leave Approvals (where user is manager/approver)
            if approval_type in ['leave', 'all']:
                # Find leaves where current employee is the manager
                leave_approvals = request.env['hr.leave'].sudo().search([
                    ('state', '=', 'confirm'),  # Waiting for approval
                    ('employee_id.parent_id', '=', employee.id),  # Employee's manager is current user
                ], limit=limit)

                for leave in leave_approvals:
                    approvals.append({
                        'id': leave.id,
                        'type': 'leave',
                        'title': f"{leave.holiday_status_id.name} - {leave.employee_id.name}",
                        'employee_id': leave.employee_id.id,
                        'employee_name': leave.employee_id.name,
                        'leave_type': leave.holiday_status_id.name,
                        'date_from': leave.request_date_from.strftime('%Y-%m-%d'),
                        'date_to': leave.request_date_to.strftime('%Y-%m-%d'),
                        'number_of_days': float(leave.number_of_days),
                        'state': leave.state,
                        'state_display': dict(leave._fields['state'].selection).get(leave.state),
                        'request_date': leave.create_date.strftime('%Y-%m-%d %H:%M:%S') if leave.create_date else None,
                        'description': leave.name or '',
                    })

            # TODO: Add other approval types (expense, purchase, etc.)

            return self._json_response(data={
                'count': len(approvals),
                'approvals': approvals
            })

        except Exception as e:
            _logger.exception("Approval list error")
            return self._json_response(error=str(e), status=500)

    @http.route('/api/v1/approval/<int:approval_id>/approve', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_approval_approve(self, approval_id, **kwargs):
        """
        Approve an Item

        POST /api/v1/approval/{approval_id}/approve
        Body: {
            "type": "leave",  // leave, expense, etc.
            "action": "approve",  // approve or refuse
            "reason": "Approved"  // optional
        }

        Response: {
            "success": true,
            "data": {"message": "Leave approved successfully"}
        }
        """
        if request.httprequest.method == 'OPTIONS':
            return self._json_response()

        try:
            user = self._authenticate()
            if not user:
                return self._json_response(error='Authentication required', status=401)

            employee = user.employee_id
            if not employee:
                return self._json_response(error='No employee record found', status=404)

            # Parse request
            body = json.loads(request.httprequest.data.decode('utf-8'))

            approval_type = body.get('type', 'leave')
            action = body.get('action', 'approve')
            reason = body.get('reason', '')

            if approval_type == 'leave':
                # Get leave
                leave = request.env['hr.leave'].sudo().browse(approval_id)

                if not leave.exists():
                    return self._json_response(error='Leave request not found', status=404)

                # Check if current employee is the approver (manager)
                if leave.employee_id.parent_id.id != employee.id:
                    return self._json_response(error='You are not authorized to approve this request', status=403)

                # Check state
                if leave.state != 'confirm':
                    return self._json_response(error='Leave is not in pending approval state', status=400)

                # Perform action
                if action == 'approve':
                    leave.action_approve()
                    message = 'Leave approved successfully'
                elif action == 'refuse':
                    leave.action_refuse()
                    if reason:
                        leave.message_post(body=f"Refused: {reason}")
                    message = 'Leave refused successfully'
                else:
                    return self._json_response(error='Invalid action. Use "approve" or "refuse"', status=400)

                return self._json_response(data={
                    'message': message,
                    'leave_id': leave.id,
                    'new_state': leave.state,
                })

            else:
                return self._json_response(error=f'Approval type "{approval_type}" not supported yet', status=400)

        except Exception as e:
            _logger.exception("Approval action error")
            return self._json_response(error=str(e), status=500)
