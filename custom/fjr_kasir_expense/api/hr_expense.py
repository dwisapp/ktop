from odoo.http import request
from odoo import http, _, fields
from odoo.exceptions import AccessDenied, UserError
from math import ceil
import base64
import json
import uuid

class HrExpense(http.Controller):

    @http.route("/api/expense", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_expense(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expenses"))

        kwargs = request.httprequest.args
        domain = [("employee_id", "=", employee_id.id)]

        if kwargs.get("description"):
            domain.append(("name", "ilike", kwargs.get("description")))
        if kwargs.get("date_from"):
            domain.append(("date", ">=", kwargs.get("date")))
        if kwargs.get("date_to"):
            domain.append(("date", "<=", kwargs.get("date")))
        if kwargs.get("status"):
            domain.append(("state", "=", kwargs.get("status")))
        if kwargs.get("date"):
            domain.append(("date", "=", kwargs.get("date")))



        order_by = kwargs.get("order", "name")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit

        expense_ids = request.env["hr.expense"].sudo().search(domain, order=order_by, limit=limit, offset=offset)
        expense_list = []
        


        for expense in expense_ids:
            expense_val = self._prepare_expense_vals(expense)
            expense_list.append(expense_val)

        total_count = request.env["hr.expense"].sudo().search_count(domain)
        total_pages = ceil(total_count / limit)
        return {
            "expenses": expense_list,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
        }
    
    @http.route("/api/expense/<int:expense_id>", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_expense_by_id(self, expense_id, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expenses"))

        expense = request.env["hr.expense"].sudo().search([
            ("id", "=", expense_id),
            ("employee_id", "=", employee_id.id)
        ], limit=1)
        if not expense:
            raise UserError(_("Expense not found or you do not have access to it."))
        expense_val = self._prepare_expense_vals(expense)
        return expense_val


    @http.route("/api/expense", type="json", auth="jwt", methods=["POST"], csrf=False)
    def create_expense(self, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expenses"))

        if not kwargs.get("description"):
            raise UserError(_("Description is required to create an expense."))
        if not kwargs.get("date"):
            raise UserError(_("Date is required to create an expense."))
        if not kwargs.get("total_amount"):
            raise UserError(_("Total amount is required to create an expense."))
        if not kwargs.get("category_id"):
            raise UserError(_("Category is required to create an expense."))
        
        expense_vals = {
            "name": kwargs.get("description"),
            "date": fields.Date.from_string(kwargs.get("date")),
            "total_amount": kwargs.get("total_amount"),
            "employee_id": employee_id.id,
            "product_id": kwargs.get("category_id"),
            "payment_mode": kwargs.get("paid_by", 'company_account'),
        }
        if kwargs.get("include_taxes"):
            taxes = request.env["account.tax"].sudo().search([
                ("id", "in", kwargs.get("include_taxes"))
            ])
            if not taxes:
                raise UserError(_("Invalid taxes provided."))
            expense_vals["tax_ids"] = [(6, 0, taxes.ids)]

        if kwargs.get("projects"):
            analytic_accounts = request.env['account.analytic.account'].sudo().search([
                ('id', 'in', kwargs.get("projects"))
            ])
            if not analytic_accounts:
                raise UserError(_("Invalid projects provided."))
            expense_vals["analytic_distribution"] = {str(account.id): 100.0 for account in analytic_accounts}

        if kwargs.get("manager_id"):
            manager = request.env['res.users'].sudo().search([
                ("id", "=", kwargs.get("manager_id"))
            ], limit=1)
            if not manager:
                raise UserError(_("Invalid manager provided."))
            expense_vals["manager_id"] = manager.id
        if kwargs.get("accounting_id"):

            accounting_user = request.env['res.users'].sudo().search([
                ("id", "=", kwargs.get("accounting_id"))
            ], limit=1)
            if not accounting_user:
                raise UserError(_("Invalid accounting user provided."))
            expense_vals["accounting_id"] = accounting_user.id

        if kwargs.get("accounting_manager_id"):
            accounting_manager = request.env['res.users'].sudo().search([
                ("id", "=", kwargs.get("accounting_manager_id"))
            ], limit=1)
            if not accounting_manager:
                raise UserError(_("Invalid accounting manager provided."))
            expense_vals["accounting_manager_id"] = accounting_manager.id


        expense = request.env["hr.expense"].sudo().create(expense_vals)
        if not expense.account_id:
            expense.account_id = request.env['ir.property']._get('property_account_expense_categ_id', 'product.category')


        expense_val = self._prepare_expense_vals(expense)
        return expense_val
    
    @http.route("/api/expense/<int:expense_id>", type="json", auth="jwt", methods=["PUT"], csrf=False)
    def update_expense(self, expense_id, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expenses"))

        expense = request.env["hr.expense"].sudo().search([
            ("id", "=", expense_id),
            ("employee_id", "=", employee_id.id)
        ], limit=1)
        expense_state_values = dict(request.env["hr.expense"]._fields['state'].selection)
        if not expense:
            raise UserError(_("Expense not found or you do not have access to it."))
        if expense.state not in ['draft', 'reported']:
            raise UserError(_("Expense is currently in status '%s', it cannot be updated.") % 
                             expense_state_values.get(expense.state))

        write_vals = {}

        if kwargs.get("description"):
            write_vals["name"] = kwargs.get("description")
        if kwargs.get("date"):
            write_vals["date"] = fields.Date.from_string(kwargs.get("date"))
        if kwargs.get("total_amount"):
            write_vals["total_amount"] = kwargs.get("total_amount")
        if kwargs.get("category_id"):
            write_vals["product_id"] = kwargs.get("category_id")
        if kwargs.get("paid_by"):
            write_vals["payment_mode"] = kwargs.get("paid_by", 'company_account')
        if kwargs.get("manager_id"):
            manager = request.env['res.users'].sudo().search([
                ("id", "=", kwargs.get("manager_id"))
            ], limit=1)
            if not manager:
                raise UserError(_("Invalid manager provided."))
            write_vals["manager_id"] = manager.id
        if kwargs.get("accounting_id"):
            accounting_user = request.env['res.users'].sudo().search([
                ("id", "=", kwargs.get("accounting_id"))
            ], limit=1)
            if not accounting_user:
                raise UserError(_("Invalid accounting user provided."))
            write_vals["accounting_id"] = accounting_user.id
        if kwargs.get("accounting_manager_id"):
            accounting_manager = request.env['res.users'].sudo().search([
                ("id", "=", kwargs.get("accounting_manager_id"))
            ], limit=1)
            if not accounting_manager:
                raise UserError(_("Invalid accounting manager provided."))
            write_vals["accounting_manager_id"] = accounting_manager.id

        if kwargs.get("include_taxes"):
            taxes = request.env["account.tax"].sudo().search([
                ("id", "in", kwargs.get("include_taxes"))
            ])
            if not taxes:
                raise UserError(_("Invalid taxes provided."))
            write_vals["tax_ids"] = [(6, 0, taxes.ids)]

        if kwargs.get("projects"):
            analytic_accounts = request.env['account.analytic.account'].sudo().search([
                ('id', 'in', kwargs.get("projects"))
            ])
            if not analytic_accounts:
                raise UserError(_("Invalid projects provided."))
            write_vals["analytic_distribution"] = {str(account.id): 100.0 for account in analytic_accounts}

        expense_val = self._prepare_expense_vals(expense)
        return expense_val
    

    @http.route("/api/expense/<int:expense_id>", type="json", auth="jwt", methods=["DELETE"], csrf=False)
    def delete_expense(self, expense_id, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expenses"))

        expense = request.env["hr.expense"].sudo().search([
            ("id", "=", expense_id),
            ("employee_id", "=", employee_id.id)
        ], limit=1)
        if not expense:
            raise UserError(_("Expense not found or you do not have access to it."))

        if expense.state in ['done', 'cancel']:
            raise UserError(_("Expense is currently in status '%s', it cannot be deleted.") % 
                             dict(request.env["hr.expense"]._fields['state'].selection).get(expense.state))
        
        
        expense.unlink()
        return _("Expense deleted successfully.")
    
    @http.route("/api/expense/<int:expense_id>/submit", type="json", auth="jwt", methods=["POST"], csrf=False)
    def submit_expense(self, expense_id, **kwargs):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expenses"))

        expense = request.env["hr.expense"].sudo().search([
            ("id", "=", expense_id),
            ("employee_id", "=", employee_id.id)
        ], limit=1)
        if not expense:
            raise UserError(_("Expense not found or you do not have access to it."))

       

        expense.action_submit_expenses()
        sheet_to_update = {}
        if expense.manager_id:
            sheet_to_update["user_id"] = expense.manager_id.id
        if expense.accounting_id:
            sheet_to_update["accounting_id"] = expense.accounting_id.id
        if expense.accounting_manager_id:
            sheet_to_update["accounting_manager_id"] = expense.accounting_manager_id.id

        if sheet_to_update:
            expense.sheet_id.write(sheet_to_update)
        expense.sheet_id.action_submit_sheet()
        expense_val = self._prepare_expense_vals(expense)
        return expense_val


    def _prepare_expense_vals(self, expense):
        state_values = dict(request.env["hr.expense"]._fields['state'].selection)
        paid_by_values = dict(request.env["hr.expense"]._fields['payment_mode'].selection)
        expense_val = {
                "id": expense.id,
                "description": expense.name,
                "report_number" : expense.sheet_id.name or '',
                "date": fields.Date.to_string(expense.date),

                "total_amount": expense.total_amount,
                "category": {
                    "id": expense.product_id.id,
                    "name": expense.product_id.name or "",
                },
                "manager": {
                    "id": expense.manager_id.id,
                    "name": expense.manager_id.name or "",
                } if expense.manager_id else {},
                "accounting": {
                    "id": expense.accounting_id.id,
                    "name": expense.accounting_id.name or "",
                } if expense.accounting_id else {},
                "accounting_manager": {
                    "id": expense.accounting_manager_id.id,
                    "name": expense.accounting_manager_id.name or "",
                } if expense.accounting_manager_id else {},

                "include_taxes": [
                    {
                        "id": tax.id,
                        "name": tax.name,
                    } for tax in expense.tax_ids
                ],
                "status" : {
                    "id": expense.state,
                    "value": state_values.get(expense.state, ""),
                },
                "paid_by": {
                    "id": expense.payment_mode,
                    "value": paid_by_values.get(expense.payment_mode, ""),
                },
                "projects": [],
                
                
            }
        if expense.analytic_distribution:
            for analytic in expense.analytic_distribution.keys():
                analytic_account = request.env['account.analytic.account'].sudo().browse(int(analytic))
                if analytic_account:
                    expense_val["projects"].append({
                        "id": analytic_account.id,
                        "name": analytic_account.name or "",
                    })
                

        return expense_val
    


    @http.route("/api/expense/get/categories", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_expense_categories(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expense Categories"))

        categories = request.env["product.product"].sudo().search([("can_be_expensed", "=", True)])
        category_list = []
        for category in categories:
            category_list.append({
                "id": category.id,
                "name": category.name,
            })
        return category_list
    
    @http.route("/api/expense/get/taxes", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_expense_taxes(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expense Taxes"))

        taxes = request.env["account.tax"].sudo().search([("type_tax_use", "=", "purchase")])
        tax_list = []
        for tax in taxes:
            tax_list.append({
                "id": tax.id,
                "name": tax.name,
            })
        return tax_list
    
    @http.route("/api/expense/get/projects", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_expense_projects(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expense Projects"))

        kwargs = request.httprequest.args
        domain = []
        if kwargs.get("name"):
            domain.append(("name", "ilike", kwargs.get("name")))
        
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit
        total_projects = request.env['account.analytic.account'].sudo().search_count(domain)
        total_pages = ceil(total_projects / limit)



        projects = request.env['account.analytic.account'].sudo().search(domain,limit=limit,order="name", offset=offset)
        project_list = []
        for project in projects:
            project_list.append({
                "id": project.id,
                "name": project.name,
            })
        return {
            "projects": project_list,
            "total_count": total_projects,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
        }
    

    @http.route("/api/expense/get/managers", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_expense_managers(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Expense Managers"))

        managers = request.env['res.users'].sudo().search([('groups_id', 'in', request.env.ref('hr_expense.group_hr_expense_team_approver').id)])
        manager_list = []
        for manager in managers:
            manager_list.append({
                "id": manager.id,
                "name": manager.name,
            })
        return manager_list
    

    @http.route("/api/expense/get/accounting_users", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_accounting_users(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Accounting Users"))

        accounting_users = request.env['res.users'].sudo().search([('groups_id', 'in', request.env.ref('fjr_kasir_expense.group_hr_expense_accounting_user').id)])
        accounting_user_list = []
        for user in accounting_users:
            accounting_user_list.append({
                "id": user.id,
                "name": user.name,
            })
        return accounting_user_list
    
    @http.route("/api/expense/get/accounting_managers", type="json", auth="jwt", methods=["GET"], csrf=False)
    def get_accounting_managers(self):
        employee_id = request.env.user.employee_ids and request.env.user.employee_ids[0]
        if not employee_id:
            raise AccessDenied(_("You are not allowed to access Accounting Managers"))

        accounting_managers = request.env['res.users'].sudo().search([('groups_id', 'in', request.env.ref('fjr_kasir_expense.group_hr_expense_accounting_manager').id)])
        accounting_manager_list = []
        for manager in accounting_managers:
            accounting_manager_list.append({
                "id": manager.id,
                "name": manager.name,
            })
        return accounting_manager_list
    
