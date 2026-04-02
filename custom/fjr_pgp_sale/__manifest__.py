# -*- coding: utf-8 -*-
{
    'name': "Custom Sales - PT PGP",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Fajar - 081268888199",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'fjr_kasir_base','sale_stock', 'fleet', 'sale_project', 'fjr_pgp_account'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',

        'views/sale_order.xml',
        'views/delivery_note.xml',
        'views/product_template.xml',
        'views/account_move.xml',

        'views/res_tempat_muat.xml',
        'views/res_tujuan_bongkar.xml',

        'wizard/wizard_change_sale_order.xml',


        'menu.xml',
    ],
    # only loaded in demonstration mode
   
}

