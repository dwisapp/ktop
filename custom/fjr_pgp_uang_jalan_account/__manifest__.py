# -*- coding: utf-8 -*-
{
    'name': "Accounting for Uang Jalan PGP",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Fajar - 081268888199",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['fjr_kasir_uang_jalan', 'account', 'fjr_pgp_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/uang_jalan.xml',
    ],
    # only loaded in demonstration mode
    
}

