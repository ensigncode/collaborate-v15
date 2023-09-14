# -*- coding: utf-8 -*-
{
    'name': "Invoice Template bg",
    'description': """
        Invoice template modifications
    """,
    'category': 'Accounting',
    'version': '15.0.1.0.0',

    'depends': ['account','base'],

    'data': [
        'report/invoice_report_template.xml',
        'report/invoice_report.xml',
        'views/res_company_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
