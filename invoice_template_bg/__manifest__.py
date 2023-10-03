# -*- coding: utf-8 -*-
{
    'name': "Invoice Template bg",
    'description': """
        Invoice template modifications
    """,
    'category': 'Accounting',
    'version': '15.0.1.0.6',

    'depends': ['base', 'account', ],

    'data': [
        'views/res_company_view.xml',
        'views/ir_actions_reports.xml',
        'report/invoice_report_template.xml',
        'report/invoice_report.xml',

    ],
    'installable': True,
    'auto_install': True
}
