# -*- coding: utf-8 -*-
{
    'name': "Export Invoice Scheme",
    'description': """
        Export Invoice Scheme
    """,
    'category': 'Accounting',
    'version': '15.0.0.0.4',
    'depends': [
            'account'
        ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_export_views.xml',
    ],
    'assets': {
        'web.assets_qweb': [],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': True
}
