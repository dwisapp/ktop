# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountPaymentRegister(models.TransientModel):
    _name = "account.payment.register"
    _inherit = ["account.payment.register", "analytic.mixin"]

    payment_difference_handling = fields.Selection(
        selection_add=[
            ("reconcile_multi_deduct", "Mark invoice as fully paid (multi deduct)")
        ],
        ondelete={"reconcile_multi_deduct": "cascade"},
    )
    deduct_residual = fields.Monetary(
        string="Remainings", compute="_compute_deduct_residual"
    )
    
    deduction_ids = fields.One2many(
        comodel_name="account.payment.deduction",
        inverse_name="payment_id",
        string="Deductions",
        copy=False,
        help="Sum of deduction amount(s) must equal to the payment difference",
    )
    deduct_analytic_distribution = fields.Json()
    payment_register_deduction_id = fields.Many2one(
        comodel_name="account.payment.register.deduction",
        string="Payment Deduction",
        copy=False,
    )

    payment_deduction_amount = fields.Monetary(
        string="Payment Deduction Amount",
    )
    tax_ids = fields.Many2many("account.tax", string="Additional Taxes")
    included_tax_line_ids = fields.One2many(
        comodel_name="account.payment.register.included.tax.line",
        inverse_name="payment_register_id",
        string="Included Tax Lines",compute="_compute_included_tax_line_ids",)
    



    @api.depends('can_group_payments')
    def _compute_group_payment(self):
        super(AccountPaymentRegister, self)._compute_group_payment()
        for rec in self.filtered(lambda r: r.can_group_payments):
            rec.group_payment = True

    @api.depends("tax_ids", "amount", "deduction_ids.amount", "deduction_ids.is_open")
    def _compute_included_tax_line_ids(self):
        for rec in self:
            included_tax_line_ids = [(5,0,0)]
            if rec.tax_ids:
                current_amount = rec.amount + sum(rec.deduction_ids.filtered(lambda d: not d.is_open).mapped("amount"))
                residual_without_taxes = sum(rec.line_ids.mapped("amount_residual"))
                proporsi = current_amount / rec.source_amount
                current_amount = residual_without_taxes * proporsi
                current_amount = round(current_amount, 2)
                amount_to_compute = rec.line_ids.move_id._get_payment_amount_without_taxes(current_amount)
                tax_totals = rec.tax_ids.compute_all(
                    amount_to_compute,
                    quantity=-1 if rec.payment_type == "inbound" else 1,
                    handle_price_include=False,
                )
                for tax in tax_totals["taxes"]:
                    included_tax_line_ids.append(
                        (0, 0, {
                            "tax_id": tax["id"],
                            "amount": tax["amount"],
                        })
                    )
            rec.included_tax_line_ids = included_tax_line_ids

                
                
            
                

    @api.depends("tax_ids")
    def _compute_amount(self):
        super(AccountPaymentRegister, self)._compute_amount()
        for wizard in self.filtered(lambda w: w.tax_ids):
            batch_result = wizard._get_batches()[0]
            amount = wizard._get_total_amount_in_wizard_currency_to_full_reconcile(batch_result)[0]
            wizard.amount = amount


    @api.depends('tax_ids')
    def _compute_from_lines(self):
        super(AccountPaymentRegister, self)._compute_from_lines()

    def _get_total_amount_in_wizard_currency_to_full_reconcile(self, batch_result, early_payment_discount=True):
        amount, mode = super(AccountPaymentRegister, self)._get_total_amount_in_wizard_currency_to_full_reconcile(batch_result, early_payment_discount=early_payment_discount)
        
        if self.tax_ids:
            amount_to_compute = self.line_ids.move_id._get_payment_amount_without_taxes(amount)
            amount_include_tax = self.tax_ids.compute_all(
                amount_to_compute,
                currency=self.currency_id,
                quantity=1,
                handle_price_include=False,
                )
            amount -= (amount_include_tax["total_excluded"] - amount_include_tax["total_included"])
        
        return amount, mode
    
    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        results = super(AccountPaymentRegister, self)._get_wizard_values_from_batch(batch_result)
        if self.tax_ids:
            source_amount = self.line_ids.move_id._get_payment_amount_without_taxes(
                results["source_amount"],
            )
            source_amount_currency = self.line_ids.move_id._get_payment_amount_without_taxes(
                results["source_amount_currency"],
            )

            source_amount_tax = self.tax_ids.compute_all(
                source_amount,
                handle_price_include=False,
                )
            
            currency_id = self.env["res.currency"].browse(
                results["source_currency_id"]
            )
            source_amount_currency_tax = self.tax_ids.compute_all(
                source_amount_currency,
                currency=currency_id,
                handle_price_include=False,
                )
            results["source_amount"] -= (source_amount_tax["total_excluded"] - source_amount_tax["total_included"])
            results["source_amount_currency"] -= (source_amount_currency_tax["total_excluded"] - source_amount_currency_tax["total_included"])
        return results
                

    @api.onchange("payment_register_deduction_id")
    def _onchange_payment_register_deduction_id(self):
        if not self.payment_register_deduction_id.line_ids:
            self.payment_register_deduction_id = False
            return

        total_amount = 0
        deduction_vals = []

        for line in self.payment_register_deduction_id.line_ids:
            amount = 0
            if line.amount_type == "percentage":
                self_amount = self.amount
                if line.before_taxes:
                    self_amount = self.line_ids.move_id._get_payment_amount_without_taxes(self_amount)
                amount = self_amount * line.amount / 100
            else:
                amount = line.amount

            

            total_amount += amount
            deduction_vals.append(
                (0, 0, {"name": line.name, "account_id": line.account_id.id, "amount": amount})
            )
        
        self.amount -= total_amount
        if self.payment_difference_handling != "reconcile_multi_deduct":
            self.payment_difference_handling = "reconcile_multi_deduct"
        self.deduction_ids = deduction_vals
        self.payment_register_deduction_id = False



    @api.onchange("payment_deduction_amount")
    def _onchange_payment_deduction_amount(self):
        if self.payment_deduction_amount:
            self.deduction_ids = [ (0, 0, { "amount": self.payment_deduction_amount})]
            self.amount -= self.payment_deduction_amount
            if self.payment_difference_handling != "reconcile_multi_deduct":
                self.payment_difference_handling = "reconcile_multi_deduct"
            self.payment_deduction_amount = False

    def _update_vals_deduction(self, moves):
        move_lines = moves.mapped("line_ids")
        analytic = {}
        [
            analytic.update(item)
            for item in move_lines.mapped("analytic_distribution")
            if item
        ]
        self.analytic_distribution = analytic

    def _update_vals_multi_deduction(self, moves):
        move_lines = moves.mapped("line_ids")
        analytic = {}
        [
            analytic.update(item)
            for item in move_lines.mapped("analytic_distribution")
            if item
        ]
        self.deduct_analytic_distribution = analytic

    @api.onchange("payment_difference", "payment_difference_handling")
    def _onchange_default_deduction(self):
        moves = self.env["account.move"]
        active_ids = self.env.context.get("active_ids", [])
        if self._context.get('active_model') == 'account.move':
            moves = self.env["account.move"].browse(active_ids)
        elif self._context.get('active_model') == 'account.move.line':
            moves = self.env["account.move.line"].browse(active_ids).move_id
        if self.payment_difference_handling == "reconcile":
            self._update_vals_deduction(moves)
        if self.payment_difference_handling == "reconcile_multi_deduct":
            self._update_vals_multi_deduction(moves)

    @api.constrains("deduction_ids", "payment_difference_handling")
    def _check_deduction_amount(self):
        prec_digits = self.env.user.company_id.currency_id.decimal_places
        for rec in self:
            if rec.payment_difference_handling == "reconcile_multi_deduct":
                deduction_without_account = rec.deduction_ids.filtered(
                    lambda l: not l.account_id and not l.is_open
                )
                if deduction_without_account:
                    raise UserError(
                        _("Please select account for deduction(s): %s")
                        % deduction_without_account.mapped("name")
                    )
                

                if (
                    float_compare(
                        rec.payment_difference,
                        sum(rec.deduction_ids.mapped("amount")),
                        precision_digits=prec_digits,
                    )
                    != 0
                ):
                    raise UserError(
                        _("The total deduction should be %s") % rec.payment_difference
                    )

    @api.depends("payment_difference", "deduction_ids.amount")
    def _compute_deduct_residual(self):
        for rec in self:
            rec.deduct_residual = rec.payment_difference - sum(
                rec.deduction_ids.mapped("amount")
            )

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        # payment difference
        if (
            not self.currency_id.is_zero(self.payment_difference)
            and self.payment_difference_handling == "reconcile"
        ):
            payment_vals["write_off_line_vals"][0][
                "analytic_distribution"
            ] = self.analytic_distribution
        # multi deduction
        elif (
            self.payment_difference
            and self.payment_difference_handling == "reconcile_multi_deduct"
        ):
            payment_vals["write_off_line_vals"] = [
                self._prepare_deduct_move_line(deduct)
                for deduct in self.deduction_ids.filtered(lambda l: not l.is_open)
            ]
            payment_vals["is_multi_deduction"] = True

        if self.tax_ids:
            quantity = -1 if self.payment_type == "inbound" else 1
            
            current_amount = self.amount
            
            for writeoff in payment_vals["write_off_line_vals"]:
                if self.payment_type == "inbound":
                    if writeoff.get("balance"):
                        current_amount += writeoff["balance"]
                else:
                    if writeoff.get("balance"):
                        current_amount -= writeoff["balance"]
                

            residual_without_taxes = sum(batch_result["lines"].mapped("amount_residual"))
            proporsi = current_amount / self.source_amount
            
            current_amount = abs(residual_without_taxes) * proporsi
            current_amount = round(current_amount, 2)

            for aml in batch_result['lines']:
                
                amount_to_convert = min(current_amount, abs(aml.amount_residual))
                amount_to_convert = aml.move_id._get_payment_amount_without_taxes(amount_to_convert)    
                tax_amount = 0
                tax_totals = self.with_context(caba_no_transition_account=True).tax_ids.compute_all(
                    amount_to_convert,
                    quantity=quantity,
                    handle_price_include=False,
                )
                for tax in tax_totals["taxes"]:
                    payment_vals["write_off_line_vals"].append(
                        {
                            "name": aml.move_id.name + " - " + tax["name"],
                            "account_id": tax["account_id"],
                            "partner_id": aml.partner_id.id,
                            "amount_currency": tax["amount"],
                            "balance": tax["amount"],
                            "analytic_distribution": self.deduct_analytic_distribution,
                        }
                    )
                    tax_amount += tax["amount"]



                current_amount -= aml.amount_residual
                if current_amount <= 0:
                    break
            # 
                

        return payment_vals

    def _prepare_deduct_move_line(self, deduct):
        conversion_rate = self.env["res.currency"]._get_conversion_rate(
            self.currency_id,
            self.company_id.currency_id,
            self.company_id,
            self.payment_date,
        )
        write_off_amount_currency = (
            deduct.amount if self.payment_type == "inbound" else -deduct.amount
        )
        write_off_balance = self.company_id.currency_id.round(
            write_off_amount_currency * conversion_rate
        )
        return {
            "name": deduct.name,
            "account_id": deduct.account_id.id,
            "partner_id": self.partner_id.id,
            "currency_id": self.currency_id.id,
            "amount_currency": write_off_amount_currency,
            "balance": write_off_balance,
            "analytic_distribution": deduct.analytic_distribution,
        }

class AccountPaymentRegisterIncludedTaxLine(models.TransientModel):
    _name = "account.payment.register.included.tax.line"
    _description = "Account Payment Register Included Tax Line"

    payment_register_id = fields.Many2one(
        comodel_name="account.payment.register",
        string="Payment Register",
        ondelete="cascade",
    )
    tax_id = fields.Many2one(
        comodel_name="account.tax", string="Tax", ondelete="restrict"
    )
    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one("res.currency", string="Currency", related="payment_register_id.currency_id")