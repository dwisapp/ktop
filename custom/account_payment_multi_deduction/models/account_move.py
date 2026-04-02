from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_payment_amount_without_taxes(self, amount):
        amount_taxes = sum(self.mapped('amount_tax'))
        if not amount_taxes:
            return amount

        # Hitung persentase pajak dengan benar
        base_amount = sum(self.mapped('amount_total')) - amount_taxes
        taxes_percentage = amount_taxes / base_amount

        return amount / (1 + taxes_percentage)

    def _get_taxes_percentage(self):
        amount_taxes = sum(self.mapped('amount_tax'))
        base_amount = sum(self.mapped('amount_total')) - amount_taxes
        if base_amount == 0:
            return 0
        return amount_taxes / base_amount


    def _get_payment_amount_with_taxes(self, amount, taxes_percentage):
        return amount * (1 + taxes_percentage)

        