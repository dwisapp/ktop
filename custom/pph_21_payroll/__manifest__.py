# -*- coding: utf-8 -*-
{
    'name': "PPh 21 Payroll",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Fajar - 081268888199",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_work_entry_contract_enterprise'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/hr.kategori.ter.csv',
        # 'data/hr.kategori.pph.csv',

        'data/hr.perhitungan.pph.csv',


        'views/hr_kategori_pph.xml',
        'views/hr_kategori_ter.xml',
        'views/hr_salary_rule.xml',

        'views/hr_employee.xml',
        'views/hr_perhitungan_pph.xml',

        'menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}