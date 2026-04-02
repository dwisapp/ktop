# -*- coding: utf-8 -*-
{
    'name': "Custom Payrol - PT PGP",

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
    'depends': ['hr_payroll', 'hr_work_entry_contract_enterprise', 'hr_holidays', 'fjr_pgp_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payroll_other_input.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/hr_salary_rule_category.xml',
        'views/hr_work_entry_type.xml',
        'views/hr_payslip.xml',
        'views/hr_payment_per_delivery.xml',
        'views/hr_payroll_structure.xml',
        'wizard/hr_payslip_employees.xml',

        'report/report_payslip.xml',
        'report/report_payslip_excel.xml',

        'menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

