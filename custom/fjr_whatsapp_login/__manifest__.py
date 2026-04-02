# -*- coding: utf-8 -*-
{
    'name': "Whatsapp Login",

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
    'depends': ['fjr_kasir_base', 'whatsapp'],


    #  'assets': {
    #     'web.assets_frontend': [
    #         'fjr_whatsapp_login/static/src/frontend/**/*'
    #     ]},
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/otp_verification.xml',
        # 'views/web_login.xml',
        # 'views/auth_signup.xml',
    ],
   
}
