# -*- coding: utf-8 -*-
# ============================================================================
# Module: Bank Ledger Report
# Model: bank.ledger.wizard (TransientModel)
# ============================================================================
# Deskripsi:
#   Wizard untuk generate Bank Ledger Report dengan filter periode dan journal.
#   User dapat melihat report dalam format tree view atau print ke PDF.
#
# Fitur:
#   - Filter by Bank Journal (domain: type='bank')
#   - Filter by Date Range (date_from - date_to)
#   - View Report: Tampilkan data dalam tree view dengan running balance
#   - Print Report: Generate PDF report
#   - Auto-calculate opening balance, closing balance, total debit/credit
#
# Author: Krakatau IT
# ============================================================================
from odoo import models, fields, api
from datetime import datetime


class BankLedgerWizard(models.TransientModel):
    """
    Wizard untuk generate Bank Ledger Report.
    Memungkinkan user memilih journal bank dan periode untuk generate report.
    """
    _name = 'bank.ledger.wizard'
    _description = 'Bank Ledger Report Wizard'

    # ========================================================================
    # FIELDS - Filter Parameters
    # ========================================================================

    journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        required=True,
        domain="[('type', '=', 'bank')]",  # Hanya journal bank
        help='Pilih journal bank yang ingin ditampilkan'
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
        default=fields.Date.context_today,
        help='Tanggal awal periode laporan'
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.context_today,
        help='Tanggal akhir periode laporan'
    )

    # ========================================================================
    # ACTION METHODS
    # ========================================================================

    def action_view_report(self):
        """
        Display report in tree view.

        Fungsi ini akan:
        1. Clear previous report lines
        2. Calculate opening balance
        3. Get transaction lines dalam periode
        4. Create report lines dengan running balance
        5. Return action untuk open tree view

        Returns:
            dict: ir.actions.act_window untuk buka tree view
        """
        self.ensure_one()

        # Clear previous report lines untuk wizard ini
        self.env['bank.ledger.report.line'].search([('wizard_id', '=', self.id)]).unlink()

        # Get opening balance (saldo awal sebelum date_from)
        opening_balance = self._get_opening_balance()

        # Get transaction lines dalam periode
        lines = self._get_transaction_lines()

        # Create report lines dengan running balance
        running_balance = opening_balance
        currency = self.journal_id.currency_id or self.env.company.currency_id
        report_lines = []

        # Loop setiap transaction line dan hitung running balance
        for line in lines:
            # Update running balance
            running_balance += line.debit - line.credit

            # Create report line record
            report_line = self.env['bank.ledger.report.line'].create({
                'wizard_id': self.id,
                'date': line.date,
                'reference': line.move_id.name or '',
                'description': line.name or '',
                'partner_id': line.partner_id.id if line.partner_id else False,
                'partner_name': line.partner_id.name if line.partner_id else '',
                'debit': line.debit,
                'credit': line.credit,
                'balance': running_balance,  # Running balance after transaction
                'currency_id': currency.id,
                'move_line_id': line.id,
            })
            report_lines.append(report_line.id)

        # Return tree view action dengan context data
        return {
            'name': f'Bank Ledger - {self.journal_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bank.ledger.report.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', report_lines)],
            'context': {
                'journal_name': self.journal_id.name,
                'account_number': self.journal_id.bank_account_id.acc_number if self.journal_id.bank_account_id else '-',
                'date_from': self.date_from.strftime('%d/%m/%Y'),
                'date_to': self.date_to.strftime('%d/%m/%Y'),
                'opening_balance': opening_balance,
                'closing_balance': running_balance,  # Closing balance = last running balance
                'default_wizard_id': self.id,
            },
            'target': 'current',
        }

    def action_print_report(self):
        """
        Generate PDF report.

        Returns:
            dict: PDF report action
        """
        self.ensure_one()

        # Get report data (lines, balances, totals)
        data = self._get_report_data()

        # Return PDF report action
        return self.env.ref('bank_ledger_report.action_bank_ledger_report').report_action(self, data=data)

    # ========================================================================
    # PRIVATE METHODS - Data Processing
    # ========================================================================

    def _get_report_data(self):
        """
        Prepare all report data including lines, balances, and totals.

        Method ini digunakan untuk generate data yang akan dicetak ke PDF.
        Data yang disiapkan:
        - Opening balance (saldo awal)
        - Transaction lines dengan running balance
        - Total debit & credit
        - Closing balance (saldo akhir)

        Returns:
            dict: Data report untuk PDF template
        """
        self.ensure_one()

        # Get opening balance (saldo sebelum date_from)
        opening_balance = self._get_opening_balance()

        # Get transaction lines dalam periode
        lines = self._get_transaction_lines()

        # Calculate running balance and totals
        running_balance = opening_balance
        total_debit = 0.0
        total_credit = 0.0

        processed_lines = []
        for line in lines:
            debit = line.debit
            credit = line.credit
            running_balance += debit - credit
            total_debit += debit
            total_credit += credit

            # Format data untuk PDF template
            processed_lines.append({
                'date': line.date,
                'reference': line.move_id.name or '',
                'description': line.name or '',
                'partner': line.partner_id.name or '',
                'debit': debit,
                'credit': credit,
                'balance': running_balance,
            })

        closing_balance = running_balance

        # Return semua data untuk PDF report
        return {
            'journal_name': self.journal_id.name,
            'account_number': self.journal_id.bank_account_id.acc_number if self.journal_id.bank_account_id else '-',
            'date_from': self.date_from.strftime('%d/%m/%Y'),
            'date_to': self.date_to.strftime('%d/%m/%Y'),
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'lines': processed_lines,
            'currency': self.journal_id.currency_id or self.env.company.currency_id,
        }

    def _get_opening_balance(self):
        """
        Calculate opening balance (total sebelum date_from).

        Opening balance = SUM(debit) - SUM(credit) untuk semua transaksi
        di journal ini sebelum date_from.

        Returns:
            float: Opening balance amount
        """
        self.ensure_one()

        domain = [
            ('journal_id', '=', self.journal_id.id),
            ('date', '<', self.date_from),  # Sebelum date_from
            ('move_id.state', '=', 'posted'),  # Hanya posted entries
            ('display_type', 'not in', ['line_section', 'line_note']),  # Exclude section/note
        ]

        move_lines = self.env['account.move.line'].search(domain)
        opening_balance = sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit'))

        return opening_balance

    def _get_transaction_lines(self):
        """
        Get transaction lines within date range.

        Mengambil semua account.move.line dalam periode date_from - date_to
        untuk journal yang dipilih.

        Returns:
            recordset: account.move.line records (sorted by date, id)
        """

        
        self.ensure_one()

        domain = [
            ('journal_id', '=', self.journal_id.id),
            ('date', '>=', self.date_from),  # Dari date_from
            ('date', '<=', self.date_to),    # Sampai date_to
            ('move_id.state', '=', 'posted'),  # Hanya posted entries
            ('display_type', 'not in', ['line_section', 'line_note']),  # Exclude section/note
        ]

        return self.env['account.move.line'].search(domain, order='date asc, id asc')
