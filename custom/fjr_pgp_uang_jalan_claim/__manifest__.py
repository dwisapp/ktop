# -*- coding: utf-8 -*-
{
    'name': "Driver Claim Uang Jalan",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fjr_kasir_uang_jalan'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',

        'views/uang_jalan_driver_claim.xml',
        'views/uang_jalan.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

