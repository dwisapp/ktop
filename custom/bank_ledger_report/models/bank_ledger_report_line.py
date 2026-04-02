# -*- coding: utf-8 -*-
# ============================================================================
# Module: Bank Ledger Report
# Model: bank.ledger.report.line (TransientModel)
# ============================================================================
# Deskripsi:
#   Model transient untuk menyimpan line/baris data laporan Bank Ledger.
#   Model ini digunakan untuk menampilkan detail transaksi bank dalam
#   format tabel pada wizard Bank Ledger Report.
#
# Fitur:
#   - Transient model (data temporary, tidak disimpan permanent)
#   - Menyimpan data per-line: tanggal, referensi, deskripsi, partner
#   - Menampilkan debit, credit, dan running balance
#   - Relasi ke account.move.line untuk tracking journal entry
#   - Auto-sorted by date ascending
#
# Author: Krakatau IT
# ============================================================================
from odoo import models, fields, api


class BankLedgerReportLine(models.TransientModel):
    """
    Transient model untuk line/baris data Bank Ledger Report.
    Setiap record merepresentasikan satu transaksi bank.
    """
    _name = 'bank.ledger.report.line'
    _description = 'Bank Ledger Report Line'
    _order = 'date asc, id asc'  # Urut berdasarkan tanggal, lalu ID

    # ========================================================================
    # FIELDS - Bank Ledger Report Line
    # ========================================================================

    # Relasi ke wizard parent
    wizard_id = fields.Many2one(
        'bank.ledger.wizard',
        string='Wizard Reference',
        ondelete='cascade',  # Auto-delete line saat wizard dihapus
        required=True
    )

    # Data transaksi
    date = fields.Date(string='Date', readonly=True)
    reference = fields.Char(string='Reference', readonly=True)
    description = fields.Char(string='Description', readonly=True)

    # Partner info
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    partner_name = fields.Char(string='Partner', readonly=True)

    # Monetary fields
    debit = fields.Monetary(
        string='Debit',
        currency_field='currency_id',
        readonly=True
    )
    credit = fields.Monetary(
        string='Credit',
        currency_field='currency_id',
        readonly=True
    )
    balance = fields.Monetary(
        string='Balance',  # Running balance
        currency_field='currency_id',
        readonly=True
    )
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    # Relasi ke journal entry line
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        readonly=True,
        help='Link to original journal entry line'
    )
