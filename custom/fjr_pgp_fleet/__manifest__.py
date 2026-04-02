# -*- coding: utf-8 -*-
{
    'name': "Custom Fleet - ERP PTPGP",

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
    'depends': ['base', 'fleet', 'fjr_kasir_base', 'stock', 'purchase', 'account_fleet'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',

        'data/sequence.xml',
        'data/ir_cron.xml',
        'views/fleet_vehicle.xml',
        'views/fleet_document_loan.xml',
        'views/fleet_document.xml',
        'views/fleet_document_type.xml',
        'views/res_config_settings.xml',
        'views/fleet_item_usage.xml',
        'views/stock_location.xml',
        'views/product_template.xml',   
        'views/stock_move.xml',
        'views/fleet_vehicle_log_services.xml',


        'wizard/wizard_return_fleet_item_usage.xml',

        'menu.xml',
    ],
    
}

