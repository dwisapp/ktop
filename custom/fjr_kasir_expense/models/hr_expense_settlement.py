from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError

class HrExpenseSettlement(models.Model):
    _name = "hr.expense.settlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Expense Settlement"

    name = fields.Char("Expense Settlement", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    date = fields.Date("Date", required=True, default=fields.Date.context_today)
    expense_id = fields.Many2one("hr.expense", "Expense (Advance)", copy=False,
                                  domain=lambda self: [('state', '=', 'done'),('product_id.advance_expense', '=', True),
                                                    '|',  ('settlement_id', '=', False), ('settlement_id', '=', self.id)])
    
    
    employee_id = fields.Many2one("hr.employee", "Employee", compute="_compute_employee_id", store=True)
    journal_settlement_id = fields.Many2one("account.journal", "Journal Settlement", required=True, default=lambda self: self.env.company.journal_settlement_expense_id)
    company_id = fields.Many2one("res.company", "Company", required=True, default=lambda self: self.env.company)
    # account_id = fields.Many2one("account.account", "Settlement Account", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approve'),
        ('need_payment', 'Need Payment'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string="Status", default="draft", tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    total_expense = fields.Monetary("Total Expense", currency_field="currency_id", compute="_compute_total_expense", store=True)
    amount = fields.Monetary("Amount", currency_field="currency_id", tracking=True, compute="_compute_total_settlement", store=True)
    move_ids = fields.One2many("account.move","settlement_expense_id" ,string="Journal Entries", copy=False)
    
    line_ids = fields.One2many(comodel_name="hr.expense.settlement.line", inverse_name='settlement_id', string="Settlement List", required=True)
    settlement_status = fields.Selection([
        ('smaller', 'Selisih Kurang'),
        ('bigger', 'Selisih Lebih'),
        ('equal', 'Clear'),
    ], string="Status Settlement", compute='_compute_total_settlement', store=True)
    amount_diff = fields.Monetary(string="Amount Difference", compute='_compute_total_settlement', store=True)

    sisa_account_id = fields.Many2one("account.account", "Countepart Account", compute="_compute_sisa_account_id", store=True, readonly=False, )
    # payment_method_line_id = fields.Many2one(
    #     comodel_name='account.payment.method.line',
    #     string="Payment Method",
    #     compute='_compute_payment_method_line_id', store=True, readonly=False,
    #     domain="[('id', 'in', selectable_payment_method_line_ids)]",
    #     help="The payment method used when the expense is paid by the company.",
    # )
    # selectable_payment_method_line_ids = fields.Many2many(
    #     comodel_name='account.payment.method.line',
    #     compute='_compute_selectable_payment_method_line_ids',
    # )
    move_count = fields.Integer("Move Count", compute="_compute_move_count")
    payment_ids = fields.One2many("account.payment", "settlement_expense_id", "Payments")

    @api.depends("line_ids",'line_ids.amount','total_expense')
    def _compute_total_settlement(self):
        for rec in self:
            rec.amount              = sum(line.amount for line in rec.line_ids)
            rec.amount_diff         = rec.total_expense - rec.amount
            status                  = 'equal'
            if rec.amount_diff != 0:
                status = 'smaller' if rec.amount < rec.total_expense else 'bigger'
            

            rec.settlement_status   = status

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("hr.expense.settlement") or _("New")
        expense = self.env["hr.expense"].browse(vals.get("expense_id"))
        if expense.settlement_id:
            raise UserError(_("Expense %s sudah memiliki settlement") % expense.name)
        res = super(HrExpenseSettlement, self).create(vals)
        expense.write({"settlement_id": res.id})
        return res
    
    def write(self, vals):
        if vals.get("expense_id"):
            expense = self.env["hr.expense"].browse(vals.get("expense_id"))
            if expense.settlement_id and expense.settlement_id != self:
                raise UserError(_("Expense %s sudah memiliki settlement") % expense.name)
            self.expense_id.write({"settlement_id": False})
            expense.write({"settlement_id": self.id})
        return super(HrExpenseSettlement, self).write(vals)
    
    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Cannot delete settled expense settlement"))
            rec.expense_id.write({"settlement_id": False})
        return super(HrExpenseSettlement, self).unlink()
    
    @api.depends('company_id')
    def _compute_selectable_payment_method_line_ids(self):
        for sheet in self:
            allowed_method_line_ids = sheet.company_id.company_expense_allowed_payment_method_line_ids
            if allowed_method_line_ids:
                sheet.selectable_payment_method_line_ids = allowed_method_line_ids
            else:
                sheet.selectable_payment_method_line_ids = self.env['account.payment.method.line'].search([
                    ('payment_type', '=', 'outbound'),
                    ('company_id', 'parent_of', sheet.company_id.id)
                ])

    @api.depends('selectable_payment_method_line_ids')
    def _compute_payment_method_line_id(self):
        for sheet in self:
            sheet.payment_method_line_id = sheet.selectable_payment_method_line_ids[:1]


    @api.depends("expense_id")
    def _compute_total_expense(self):
        for rec in self:
            rec.total_expense = rec.expense_id.total_amount 

    @api.depends("move_ids", "payment_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(rec.move_ids) 

    @api.depends("expense_id")
    def _compute_employee_id(self):
        for rec in self:
            rec.employee_id = rec.expense_id.employee_id.id


    @api.depends("amount", "total_expense")
    def _compute_sisa_account_id(self):
        for rec in self:
            sisa_account_id = False
            if rec.amount < rec.total_expense:
                sisa_account_id = rec.employee_id.sudo().work_contact_id.property_account_receivable_id.id
            elif rec.amount > rec.total_expense:
                sisa_account_id = rec.employee_id.sudo().work_contact_id.property_account_payable_id.id
            rec.sisa_account_id = sisa_account_id

    def action_confirm(self):
       
        self.write({"state": "confirm"})

    def action_draft(self):
        if self.expense_id.settlement_id:
            self.write({"expense_id": False})
        else:
            self.expense_id.write({"settlement_id": self.id})

        self.write({"state": "draft"})

    def action_cancel(self):
        if self.move_ids:
            self.move_ids.button_cancel()
            self.move_ids.unlink()
        if self.payment_ids:
            self.payment_ids.action_cancel()
            self.payment_ids.unlink()
        self.expense_id.write({"settlement_id": False})
        self.write({"state": "cancel"})

    def action_approve(self):
        self.write({"state": "approve"})

    def action_open_journal_entry(self):
        move_ids = self.move_ids + self.payment_ids.move_id
        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_move_journal_line")
        if len(move_ids) > 1:
            action["domain"] = [("id", "in", move_ids.ids)]
        elif len(move_ids) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = move_ids.id
        return action
    
    def action_open_payment(self):
        payment_ids = self.payment_ids
        
        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_account_payments")
        if len(payment_ids) > 1:
            action["domain"] = [("id", "in", payment_ids.ids)]
        elif len(payment_ids) == 1:
            action["res_id"] = self.payment_ids.id
            action["views"] = [(False, "form")]
        return action
    
    def action_post_settlement(self):
        status_to_write = "done"

        line_ids = []
        for l in self.line_ids:
            line_ids.append((0, 0, {
                "name"          : f'{self.employee_id.name} at {self.name} :  {l.name}',
                "account_id"    : l.account_id.id,
                "debit"         : l.amount,
                "credit"        : 0,
            }))

        line_ids.append((0, 0, {
            "name"          : f'{self.employee_id.name} at {self.name} :  {l.name}',
            "account_id"    : self.expense_id.account_id.id,
            "debit"         : 0,
            "credit"        : self.total_expense,
        }))

        # if have diff
        if self.amount_diff != 0:
            line_ids.append((0, 0, {
                "name"          : f'{self.employee_id.name} at {self.name} :  {l.name}',
                "account_id"    : self.sisa_account_id.id,
                "debit"         : abs(self.amount_diff) if self.amount_diff > 0 else 0,
                "credit"        : abs(self.amount_diff) if self.amount_diff < 0 else 0,
            }))

            status_to_write = "need_payment"
        
        move_id = self.env["account.move"].create({
            "journal_id": self.journal_settlement_id.id,
            "date": self.date,
            "ref": f'{self.employee_id.name}: {self.name}',
            "line_ids": line_ids,
            "settlement_expense_id": self.id,
        })
        move_id.action_post()

        self.write({"state": status_to_write, "move_ids": [(4, move_id.id)]})
        return True
        # return self.action_open_journal_entry()

    def action_create_payment(self):
        return self.move_ids.with_context(settlement_expense_id=self.id,default_partner_bank_id=(
            self.employee_id.sudo().bank_account_id.id if len(self.employee_id.sudo().bank_account_id.ids) <= 1 else None
        )).action_register_payment()
    

    
    def recompute_payment_state(self):
        for rec in self:

            posted_payment_ids = rec.payment_ids.filtered(lambda p: p.state == 'posted')
            total_amount = sum(posted_payment_ids.mapped('amount'))
            if abs(total_amount) >= abs(rec.amount_diff):
                rec.write({
                    'state' : 'done'
                })
            else:
                rec.write({
                    'state' : 'need_payment'
                })





class HrExpenseSettlementLine(models.Model):
    _name = "hr.expense.settlement.line"
    _description = "Expense Settlement Line"

    settlement_id       = fields.Many2one(comodel_name="hr.expense.settlement", string="Settlement")
    
    
    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account",
        compute='_compute_product_name_account', precompute=True, store=True, readonly=False,
        check_company=True,
        domain="[('account_type', 'not in', ('asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card'))]",
        help="An expense account is expected",
    )


    product_id          = fields.Many2one("product.product", "Category", check_company=True,
                                                    domain=[('can_be_expensed', '=', True), ("advance_expense",'=', False)])
    name                = fields.Char(string="Description", required=True, compute="_compute_product_name_account", precompute=True, store=True, readonly=False, )
    amount              = fields.Monetary(string="Amount", required=True, currency_field="currency_id")
    currency_id         = fields.Many2one(comodel_name="res.currency", related='settlement_id.currency_id', store=True)
    company_id          = fields.Many2one("res.company", related="settlement_id.company_id")


    @api.depends('product_id', 'company_id')
    def _compute_product_name_account(self):
        for _expense in self:
            expense = _expense.with_company(_expense.company_id)
            if not expense.product_id:
                expense.account_id = self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
                expense.name = ""
                continue
            account = expense.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                expense.account_id = account
            expense.name = expense.product_id.name
    