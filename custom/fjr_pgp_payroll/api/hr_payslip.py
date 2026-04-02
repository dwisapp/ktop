from odoo.http import request, content_disposition
from odoo.tools.safe_eval import safe_eval
from odoo import http, _, fields
from odoo.exceptions import AccessDenied, UserError
from math import ceil
import base64
import json
import uuid
from PyPDF2 import PdfFileReader, PdfFileWriter
import io

class Hrpayslip(http.Controller):
    
    @http.route('/api/payslip', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_payslip(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access payslip"))

        kwargs = request.httprequest.args
        domain = [("employee_id", "=", employee_id.id)]
        if kwargs.get("reference"):
            domain.append(("number", "ilike", kwargs.get("reference")))
        if kwargs.get("date_from"):
            domain.append(("date_from", ">=", kwargs.get("date_from")))
        if kwargs.get("date_to"):
            domain.append(("date_to", "<=", kwargs.get("date_to")))
        if kwargs.get("status"):
            domain.append(("status", "=", kwargs.get("status")))

        order_by = kwargs.get("order", "number")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit
        payslips = request.env["hr.payslip"].search(domain, order=order_by, limit=limit, offset=offset)

        payslip_list = []
        total_count = payslips.search_count(domain)
        state_values = dict(request.env["hr.payslip"]._fields['state'].selection)

        for payslip in payslips:
            payslip_list.append({
                "id": payslip.id,
                "name": payslip.name,
                "reference": payslip.number,
                "date_from": fields.Date.to_string(payslip.date_from),
                "date_to": fields.Date.to_string(payslip.date_to),
                "status": {
                    "id": payslip.state,
                    "value": state_values.get(payslip.state),
                },
                "amount_total": payslip.net_wage,
            })
        return {
            "payslips": payslip_list,
            "total_count": total_count,
            "page": page,
            "total_pages": ceil(total_count / limit) or 1,
            "limit": limit,
        }
    

    @http.route('/api/payslip/<int:payslip_id>', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_payslip_by_id(self, payslip_id):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access payslip"))
        
        payslip = request.env["hr.payslip"].sudo().browse(payslip_id)
        if not payslip or payslip.employee_id.id != employee_id.id:
            raise AccessDenied(_("You are not allowed to access this payslip"))


        state_values = dict(request.env["hr.payslip"]._fields['state'].selection)



        salary_components = []
        for category, lines in payslip._get_salary_rule_in_print_payslip().items():
            salary_components.append({
                "category" : category.name,
                "items": [
                    {
                        "name": line.name,
                        "amount": line.total,
                    } for line in lines
                ],
                "total": sum(line.total for line in lines),
            })


        return {
            "id": payslip.id,
            "name": payslip.name,
            "reference": payslip.number,
            "date_from": fields.Date.to_string(payslip.date_from),
            "date_to": fields.Date.to_string(payslip.date_to),
            "status": {
                "id": payslip.state,
                "value": state_values.get(payslip.state),
            },
            "amount_total": payslip.net_wage,
            "komisi_per_delivery" : [
                {
                    "description": komisi.payment_per_delivery_id.display_name,
                    "quantity": komisi.quantity,
                    "amount": komisi.amount,
                    "amount_total": komisi.amount_total,
                } for komisi in payslip.payment_per_delivery_ids
            ],
            "salary_components" : salary_components,
        }
    

    @http.route(["/api/payslip/print/<int:payslip_id>"], type='http', auth='jwt', methods=['GET'], csrf=False)
    def get_payroll_report_print(self, payslip_id):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access payslip"))
        
        
        payslip = request.env['hr.payslip'].sudo().search([
            ('id', '=', payslip_id),
            ('employee_id', '=', employee_id.id)
        ], limit=1)
        if not payslip:
            raise AccessDenied(_("You are not allowed to access this payslip"))
    

        

        pdf_writer = PdfFileWriter()
        payslip_reports = payslip._get_pdf_reports()

        for report, slips in payslip_reports.items():
            for payslip in slips:
                pdf_content, _ = request.env['ir.actions.report'].\
                    with_context(lang=payslip.employee_id.lang or payslip.env.lang).\
                    sudo().\
                    _render_qweb_pdf(report, payslip.id, data={'company_id': payslip.company_id})
                reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

                for page in range(reader.getNumPages()):
                    pdf_writer.addPage(reader.getPage(page))

        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()

        report_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})


        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', content_disposition(report_name + '.pdf'))
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)