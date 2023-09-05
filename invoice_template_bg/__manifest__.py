# -*- coding: utf-8 -*-
{
    'name': "Invoice Template bg",
    'description': """
        Invoice template modifications
    """,
    'category': 'Accounting',
    'version': '15.0.1.0.0',

    'depends': ['account'],

    'data': [
        'views/account_report_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
