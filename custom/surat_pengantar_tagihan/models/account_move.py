# -*- coding: utf-8 -*-
# ============================================================================
# Module: Surat Pengantar Tagihan
# Model: account.move (Inherit)
# ============================================================================
# Deskripsi:
#   Extend model account.move untuk menambahkan field-field yang diperlukan
#   dalam pembuatan Surat Pengantar Tagihan.
#
# Fitur:
#   - Field title_surat (judul surat yang tampil di header PDF)
#   - Field perihal, kepada_yth, isi_surat, catatan_tambahan
#   - Field penanggung_jawab (Many2one ke hr.employee)
#   - Field jabatan (auto-fill dari job_id karyawan)
#   - Field tanggal_surat (default = hari ini)
#
# Author: Krakatau IT
# Ref: FS_2.035
# ============================================================================
from odoo import models, fields, api, _
from datetime import date


class AccountMove(models.Model):
    """
    Extend account.move untuk menambahkan field surat pengantar tagihan.
    Field ini digunakan saat mencetak surat pengantar invoice.
    """
    _inherit = 'account.move'

    # ========================================================================
    # FIELDS - Surat Pengantar Tagihan
    # ========================================================================
    # Field-field di bawah ini digunakan untuk mengisi data pada report
    # Surat Pengantar Tagihan yang dicetak dari Customer Invoice

    nomor_surat = fields.Char(
        string='Nomor Surat',
        help='Nomor surat pengantar tagihan (berbeda dari nomor invoice)'
    )

    title_surat = fields.Char(
        string='Judul Surat',
        help='Judul surat yang tampil di header PDF (di bawah logo)',
        default='SURAT PENGANTAR TAGIHAN'
    )

    perihal = fields.Char(
        string='Perihal',
        help='Judul atau perihal dari surat pengantar tagihan'
    )

    kepada_yth = fields.Text(
        string='Kepada Yth.',
        help='Tujuan surat pengantar tagihan'
    )

    isi_surat = fields.Text(
        string='Isi Surat',
        help='Isi atau body dari surat pengantar tagihan'
    )

    catatan_tambahan = fields.Text(
        string='Catatan Tambahan',
        help='Informasi tambahan yang perlu disampaikan'
    )

    penanggung_jawab = fields.Many2one(
        'hr.employee',
        string='Penanggung Jawab',
        help='Nama karyawan yang bertanggung jawab dan menandatangani surat'
    )

    jabatan = fields.Char(
        string='Jabatan',
        help='Jabatan dari penanggung jawab surat'
    )

    tanggal_surat = fields.Date(
        string='Tanggal Surat',
        default=fields.Date.context_today,
        help='Tanggal pembuatan surat pengantar'
    )

    # ========================================================================
    # ONCHANGE METHODS
    # ========================================================================

    @api.onchange('penanggung_jawab')
    def _onchange_penanggung_jawab(self):
        """
        Auto-fill jabatan ketika penanggung jawab dipilih.

        Ketika user memilih penanggung jawab (hr.employee),
        field jabatan akan otomatis terisi dengan job_id dari karyawan tersebut.
        Ini memudahkan user agar tidak perlu mengisi jabatan secara manual.

        Returns:
            None: Method ini mengupdate field 'jabatan' secara langsung
        """
        if self.penanggung_jawab and self.penanggung_jawab.job_id:
            # Ambil nama jabatan dari job_id employee
            self.jabatan = self.penanggung_jawab.job_id.name
        else:
            # Reset jabatan jika penanggung jawab dikosongkan
            self.jabatan = False
