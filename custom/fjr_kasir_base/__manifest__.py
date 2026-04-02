# -*- coding: utf-8 -*-
{
    'name': "PTPGP - Custom Base",

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
    'depends': ['base', 'base_setup', 'web', 'portal', 'hr', 'auth_api_key'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/res_company.xml',
        'views/auto_close.xml',
        'views/res_partner.xml',
        'views/kapal_kapal.xml',
        'views/hr_employee.xml',
        'views/res_bank.xml',

        'wizard/wizard_global_reason.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'fjr_kasir_base/static/src/frontend/js/**/*',
            "fjr_kasir_base/static/src/frontend/js/auto_close.js"
        ],
    },
}

