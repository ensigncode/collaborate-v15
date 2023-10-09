# -*- coding: utf-8 -*-
{
    'name': "Invoice Template bg",
    'description': """
        Invoice template modifications
    """,
    'category': 'Accounting',
    'version': '15.0.1.0.8',

    'depends': ['base', 'account', ],
    'license': 'LGPL-3',
    'data': [
        'views/res_company_view.xml',
        'views/ir_actions_reports.xml',
        'views/account_move_views.xml',
        'report/invoice_report_template.xml',
        'report/invoice_report.xml',

    ],
    'installable': True,
    'auto_install': True
}
