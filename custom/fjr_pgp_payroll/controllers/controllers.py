# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from io import BytesIO
import xlsxwriter
import re
from itertools import groupby
from collections import defaultdict


from odoo.http import request, route, Controller, content_disposition
from odoo.tools.safe_eval import safe_eval


class HrPayroll(Controller):

    @route(["/print/payslips-excel"], type='http', auth='user')
    def get_payroll_report_print(self, list_ids='', **post):
        if not request.env.user.has_group('hr_payroll.group_hr_payroll_user') or not list_ids or re.search("[^0-9|,]", list_ids):
            return request.not_found()
        
        ids = [int(s) for s in list_ids.split(',')]
        payslips = request.env['hr.payslip'].browse(ids)
        payslips = payslips.sorted(key=lambda x: x.struct_id.id)
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        row_header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        comma_format = workbook.add_format({'num_format': '#,##0'})

        duplicate = 1
        for struct_id, group in groupby(payslips, key=lambda x: x.struct_id):
            
            payslip_to_add = defaultdict(lambda: defaultdict(float))
            line_to_display = []
            try:
                worksheet = workbook.add_worksheet(struct_id.name)
            except:
                while True:
                    new_name = f"{struct_id.name} ({duplicate})"
                    try:
                        worksheet = workbook.add_worksheet(new_name)
                        duplicate += 1
                        break
                    except:
                        duplicate += 1

            for payslip in group:
                for line in payslip.line_ids.filtered(lambda l: l.appears_on_payslip):
                    if line.salary_rule_id not in line_to_display:
                        line_to_display.append(line.salary_rule_id)
                    payslip_to_add[payslip][line.salary_rule_id] += line.total
            worksheet.set_row(0, 25)
            start_writing_line_column = 9

            


            for line in line_to_display:
                worksheet.write(0, start_writing_line_column + line_to_display.index(line)+1, line.name, row_header)
            
            worksheet.write(0, 0, 'Salary Slip No.', row_header)
            worksheet.write(0, 1, 'Employee NIK', row_header)
            worksheet.write(0, 2, 'Employee Name', row_header)
            worksheet.write(0, 3, 'Bank Account No.', row_header)
            worksheet.write(0, 4, 'Bank Name', row_header)
            worksheet.write(0, 5, 'Date of Joining', row_header)
            worksheet.write(0, 6, 'Department', row_header)
            worksheet.write(0, 7, 'Job Title', row_header)
            worksheet.write(0, 8, 'Start Date', row_header)
            worksheet.write(0, 9, 'End Date', row_header)
            
            current_row = 1
            for payslip, lines in payslip_to_add.items():
                worksheet.write(current_row, 0, payslip.number)
                worksheet.write(current_row, 1, payslip.employee_id.barcode or '')
                worksheet.write(current_row, 2, payslip.employee_id.name or '')
                worksheet.write(current_row, 3, payslip.employee_id.employee_payroll_bank_acc_number or '')
                worksheet.write(current_row, 4, payslip.employee_id.employee_payroll_bank_id.name or '')
                worksheet.write(current_row, 5, payslip.contract_id.date_start.strftime('%d-%m-%Y') if payslip.contract_id.date_start else '')
                worksheet.write(current_row, 6, payslip.employee_id.department_id.name or '')
                worksheet.write(current_row, 7, payslip.employee_id.job_id.name)
                worksheet.write(current_row, 8, payslip.date_from.strftime('%d-%m-%Y'))
                worksheet.write(current_row, 9, payslip.date_to.strftime('%d-%m-%Y'))




                for line in line_to_display:
                    worksheet.write(current_row, start_writing_line_column + line_to_display.index(line)+1, lines[line], comma_format)
                current_row += 1
            
            
        workbook.close()
        
        fp.seek(0)

        filename = "Salary Breakdown - %s - %s.xlsx" % (payslips[0].date_from.strftime('%d-%m-%Y'), payslips[0].date_to.strftime('%d-%m-%Y'))

        return request.make_response(
            fp.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=%s' % filename)
            ]
        )

            


              


        

