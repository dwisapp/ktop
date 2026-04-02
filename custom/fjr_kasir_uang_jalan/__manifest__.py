# -*- coding: utf-8 -*-
{
    'name': "Uang Jalan",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Fajar - 081268888199",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [ 'fleet', 'whatsapp', 'fjr_kasir_base', 'fjr_pgp_sale'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/uang_jalan.xml',
        'views/tipe_uang_jalan.xml',
        'views/uang_jalan_category.xml',
        'views/uang_jalan_jenis_barang.xml',
        'views/rute_uang_jalan.xml',
        'views/sale_order.xml',
        'views/delivery_note.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',


        'wizard/wizard_verifikasi_bca.xml',


        'menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
