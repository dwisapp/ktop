# -*- coding: utf-8 -*-
{
    'name': 'Surat Pengantar Tagihan',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Reports',
    'summary': 'Cetak Surat Pengantar Tagihan dari Customer Invoice',
    'description': """
Surat Pengantar Tagihan (FS_2.035)
===================================
Modul ini menambahkan fitur untuk mencetak Surat Pengantar Tagihan
yang terhubung dengan Customer Invoice.

Fitur Utama:
------------
* Tambahkan field surat pengantar di invoice (perihal, kepada yth, isi surat, dll)
* Tombol "Cetak Surat Pengantar Tagihan" di form invoice
* Report PDF dengan format surat resmi
* Auto-fill data dari invoice dan karyawan
* Support untuk invoice dan credit note (out_invoice, out_refund)

Akses:
------
* Hanya untuk group Accounting Invoice (account.group_account_invoice)
* Field dapat diedit oleh Accounting Manager

Referensi:
----------
Functional Specification: FS_2.035
Module: Accounting
    """,
    'author': 'Krakatau IT',
    'company': 'Krakatau IT Solutions',
    'maintainer': 'Team KIT',
    'website': 'https://www.krakatau-it.co.id',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'hr',
    ],
    'data': [
        # Reports (harus di-load terlebih dahulu karena direferensikan di view)
        'report/report_surat_pengantar_tagihan.xml',

        # Views
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
