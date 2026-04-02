from odoo.http import request
from odoo import http, _, fields
from odoo.exceptions import AccessDenied, UserError
from math import ceil
import base64
import json
import uuid

class HrLeave(http.Controller):

    def _get_timestamp(self, date):
        return fields.Datetime.context_timestamp(request.env.user, date).strftime("%d-%m-%Y %H:%M:%S")

    
    @http.route("/api/timeoff", type="json", auth="jwt", methods=["GET"])
    def get_timeoff(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access time off"))

        kwargs = request.httprequest.args
        domain = [("employee_id", "=", employee_id.id)]
        
        
        if kwargs.get("description"):
            domain.append(("name", "ilike", kwargs.get("name")))
        if kwargs.get("date_from"):
            domain.append(("date_from", ">=", kwargs.get("date_from")))
        if kwargs.get("date_to"):
            domain.append(("date_to", "<=", kwargs.get("date_to")))
        if kwargs.get("status"):
            domain.append(("status", "=", kwargs.get("status")))

        order_by = kwargs.get("order", "name")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit
        timeoff_ids = request.env["hr.leave"].sudo().search(domain, order=order_by, limit=limit, offset=offset)
        
        timeoff_list = []
        total_count = timeoff_ids.search_count(domain)
        state_values = dict(request.env["hr.leave"]._fields['state'].selection)
        for timeoff in timeoff_ids:
            timeoff_list.append({
                "id": timeoff.id,
                "time_off_type": {
                    "id": timeoff.holiday_status_id.id,
                    "name": timeoff.holiday_status_id.name,
                },
                "description": timeoff.name or '',
                "status": {
                    "id": timeoff.state,
                    "value": state_values.get(timeoff.state),
                },
                "date_from": self._get_timestamp(timeoff.date_from),
                "date_to": self._get_timestamp(timeoff.date_to),
                "duration": timeoff.duration_display,
            })
        return {
            "timeoffs": timeoff_list,
            "total": total_count,
            "page" : page,
            "total_page" : ceil(total_count / limit) or 1,
            "limit" : limit,
        }
    

    @http.route("/api/timeoff/<int:timeoff_id>", type="json", auth="jwt", methods=["GET"])
    def get_timeoff_by_id(self, timeoff_id):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access time off"))

        timeoff = request.env["hr.leave"].sudo().browse(timeoff_id)
        if not timeoff or timeoff.employee_id.id != employee_id.id:
            raise AccessDenied(_("You are not allowed to access this time off"))

        state_values = dict(request.env["hr.leave"]._fields['state'].selection)
        return {
            "id": timeoff.id,
            "time_off_type": {
                "id": timeoff.holiday_status_id.id,
                "name": timeoff.holiday_status_id.name,
            },
            "description": timeoff.name or '',
            "status": {
                "id": timeoff.state,
                "value": state_values.get(timeoff.state),
            },
            "date_from": self._get_timestamp(timeoff.date_from),
            "date_to": self._get_timestamp(timeoff.date_to),
            "duration": timeoff.duration_display,
            "supported_attachment_ids": [
                {
                    "id": attachment.id,
                    "name": attachment.name,
                    "url": "%sattachment/%s" % (request.httprequest.url_root, attachment.access_token),
                    "mimetype": attachment.mimetype,
                } for attachment in timeoff.supported_attachment_ids
            ],
        }
    
    @http.route("/api/timeoff-type", type="json", auth="jwt", methods=["GET"])
    def get_timeoff_type(self):
        kwargs = request.httprequest.args
        domain = [
            '|',
                ('requires_allocation', '=', 'no'),
                ('has_valid_allocation', '=', True),
                ('time_type', '=', 'leave'),
        ]
        if kwargs.get("name"):
            domain.append(("name", "ilike", kwargs.get("name")))
        
        order_by = kwargs.get("order", "name")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit
        timeoff_type_ids = request.env["hr.leave.type"].sudo().search(domain, order=order_by, limit=limit, offset=offset)
        
        timeoff_type_list = []
        total_count = timeoff_type_ids.search_count(domain)
        for timeoff_type in timeoff_type_ids:
            timeoff_type_list.append({
                "id": timeoff_type.id,
                "name": timeoff_type.name,
                "support_document" : timeoff_type.support_document,

            })
        return {
            "time_off_types": timeoff_type_list,
            "total": total_count,
            "page" : page,
            "total_page" : ceil(total_count / limit) or 1,
            "limit" : limit,
        }
    
    @http.route("/api/timeoff", type="json", auth="jwt", methods=["POST"])
    def create_timeoff(self, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access time off"))

        timeoff_type = kwargs.get("time_off_type")
        description = kwargs.get("description")
        date_from = kwargs.get("date_from")
        date_to = kwargs.get("date_to")
        if not timeoff_type:
            raise UserError(_("Time off type is required"))
        if not description:
            raise UserError(_("Description is required"))
        if not date_from:
            raise UserError(_("Date from is required"))
        if not date_to:
            raise UserError(_("Date to is required"))
        if date_from > date_to:
            raise UserError(_("Date from must be less than date to"))

        timeoff_type_id = request.env["hr.leave.type"].sudo().search([("id", "=", timeoff_type),
                                                                      '|', ("requires_allocation", "=", "no"), ("has_valid_allocation", "=", True)])
        if not timeoff_type_id:
            raise UserError(_("Time off type not found or not valid"))

        timeoff = request.env["hr.leave"].sudo().create({
            "holiday_status_id": timeoff_type_id.id,
            "holiday_type": "employee",
            "name": description,
            "employee_id": employee_id.id,
            "request_date_from": date_from,
            "request_date_to": date_to,
        })
        
        state_values = dict(request.env["hr.leave"]._fields['state'].selection)
        return {
            "id": timeoff.id,
            "time_off_type": {
                "id": timeoff.holiday_status_id.id,
                "name": timeoff.holiday_status_id.name,
            },
            "description": timeoff.name or '',
            "status": {
                "id": timeoff.state,
                "value": state_values.get(timeoff.state),
            },
            "date_from": self._get_timestamp(timeoff.date_from),
            "date_to": self._get_timestamp(timeoff.date_to),
            "duration": timeoff.duration_display,
            
        }
    

    @http.route("/api/timeoff/<int:timeoff_id>", type="json", auth="jwt", methods=["PUT"])
    def update_timeoff(self, timeoff_id, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access time off"))

        timeoff = request.env["hr.leave"].sudo().search([("id", "=", timeoff_id), 
                                                        ("employee_id", "=", employee_id.id)])
        if not timeoff:
            raise AccessDenied(_("You are not allowed to access this time off"))

        timeoff_type = kwargs.get("time_off_type")
        description = kwargs.get("description")
        date_from = kwargs.get("date_from") or timeoff.request_date_from
        date_to = kwargs.get("date_to") or timeoff.request_date_to
        write_vals = {}
        if timeoff_type:
            timeoff_type_id = request.env["hr.leave.type"].sudo().search([("id", "=", timeoff_type),
                                                                          '|', ("requires_allocation", "=", "no"), ("has_valid_allocation", "=", True)])
            if not timeoff_type_id:
                raise UserError(_("Time off type not found or not valid"))
            write_vals["holiday_status_id"] = timeoff_type_id.id
        
        if description:
            write_vals["name"] = description
        if date_from:
            write_vals["request_date_from"] = date_from
        if date_to:
            write_vals["request_date_to"] = date_to
        if date_from and date_to and date_from > date_to:
            raise UserError(_("Date from must be less than date to"))

        
        timeoff.sudo().write(write_vals)
        
        state_values = dict(request.env["hr.leave"]._fields['state'].selection)
        return {
            "id": timeoff.id,
            "time_off_type": {
                "id": timeoff.holiday_status_id.id,
                "name": timeoff.holiday_status_id.name,
            },
            "description": timeoff.name or '',
            "status": {
                "id": timeoff.state,
                "value": state_values.get(timeoff.state),
            },
            "date_from": self._get_timestamp(timeoff.date_from),
            "date_to": self._get_timestamp(timeoff.date_to),
            "duration": timeoff.duration_display,
        }
    

    @http.route("/api/timeoff/<int:timeoff_id>/upload-attachment", auth="jwt", type="http", methods=["POST"], csrf=False)
    def time_off_upload_attachment(self, timeoff_id, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access time off"))

        timeoff = request.env["hr.leave"].sudo().search([("id", "=", timeoff_id), 
                                                        ("employee_id", "=", employee_id.id)])
        if not timeoff:
            raise AccessDenied(_("You are not allowed to access this time off"))
        
        if 'file' not in request.httprequest.files:
            print("request.httprequest.files", request.httprequest.files)
            return json.dumps({
                "status": "error",
                "message": "File not found",
            })
        
        file = request.httprequest.files['file']
        if not file:
            raise UserError(_("File is required"))
        
        attachment = request.env['ir.attachment'].sudo().create({
            'name': file.filename,
            'type': 'binary',
            'res_model': 'hr.leave',
            'res_id': timeoff.id,
            'datas': base64.b64encode(file.read()),
            'mimetype': file.content_type,
            'access_token': str(uuid.uuid4()),
        })
        timeoff.write({
            'supported_attachment_ids': [(4, attachment.id)],
        })

        base_url = request.httprequest.url_root 
        
        return json.dumps({
            "status": "success",
            "message": "Attachment uploaded successfully",
            "attachment": {
                "id": attachment.id,
                "name": attachment.name,
                "url": "%sattachment/%s" % (base_url,attachment.access_token),
                "mimetype": attachment.mimetype,
            }
        })
    

    @http.route("/api/timeoff/<int:timeoff_id>/attachment/<int:attachment_id>", type="json", auth="jwt", methods=["DELETE"])  
    def time_off_delete_attachment(self, timeoff_id, attachment_id):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access time off"))

        timeoff = request.env["hr.leave"].sudo().search([("id", "=", timeoff_id), 
                                                        ("employee_id", "=", employee_id.id)])
        if not timeoff:
            raise AccessDenied(_("You are not allowed to access this time off"))
        
        attachment = request.env['ir.attachment'].sudo().search([("id", "=", attachment_id), 
                                                                  ("res_model", "=", "hr.leave"), 
                                                                  ("res_id", "=", timeoff.id)])
        if not attachment:
            raise AccessDenied(_("You are not allowed to access this attachment"))
        
        attachment.sudo().unlink()
        return "Attachment deleted successfully"