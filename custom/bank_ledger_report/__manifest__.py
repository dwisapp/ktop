{
    'name': 'Bank Ledger (Rekening Koran)',
    'version': '17.0.1.0.0',
    'summary': 'Laporan mutasi bank seperti rekening koran',
    'description': '''
        Bank Ledger Report Module
        ==========================
        Menambahkan menu Bank Ledger pada menu Reporting dengan wizard filter dan report PDF seperti rekening koran.

        Features:
        ---------
        * Filter by bank journal and date range
        * Optional filter by specific bank account
        * Display opening balance, closing balance, and running balance
        * Professional PDF report with proper currency formatting
        * Summary section with total debit, credit, and closing balance
    ''',
    'author': 'Krakatau IT',
    'company': 'Krakatau IT Solutions',
    'maintainer': 'Team KIT',
    'website': 'https://www.krakatau-it.co.id',
    'license': 'AGPL-3',
    'category': 'Accounting/Reporting',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/bank_ledger_report_view.xml',
        'wizard/bank_ledger_wizard_view.xml',
        'views/bank_ledger_menu.xml',
        'reports/bank_ledger_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
