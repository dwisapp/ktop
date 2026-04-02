# -*- coding: utf-8 -*-
{
    'name': "Integrasi Jasa ERP",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Fajar - 0812 6888 8199",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'fjr_kasir_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/erp_sales_order.xml',
        'views/res_partner.xml',
        'views/erp_delivery_note.xml',
        'views/res_config_settings.xml',



        "menu.xml",
       
    ],
    # only loaded in demonstration mode
    # 'assets': {
    #     'web.assets_backend': [
    #         'fjr_kasir_jasa_erp/static/src/js/*.js',
    #         'fjr_kasir_jasa_erp/static/src/xml/*.xml',
    #     ],
    # },
}
