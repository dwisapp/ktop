# -*- coding: utf-8 -*-
{
    'name': "Custom Accounting - PT. PGP",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Fajar - 0812 6888 8199",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fjr_kasir_base', 'account', 'account_accountant', 'account_asset'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',



        'views/account_move.xml',
        'views/account_asset.xml',
        'views/account_term_condition.xml',
        'views/res_partner.xml',
        'views/account_journal.xml',
        'views/account_bank_statement_line.xml',



        'report/account_move_report.xml',
        'wizard/account_asset_create_journal_entry.xml',
        
        
        'menu.xml',
    ],


    'assets' : {
        'web.assets_backend': [
            'fjr_pgp_account/static/src/**/*',
        ],
    }
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

