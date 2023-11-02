# -*- coding: utf-8 -*-
{
    'name': "Export POS Scheme",
    'description': """
        Export POS Scheme
    """,
    'category': 'Accounting',
    'version': '15.0.0.0.1',
    'depends': [
            'point_of_sale'
        ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pos_export_views.xml',
    ],
    'assets': {
        'web.assets_qweb': [],
    },
    'installable': True,
    'auto_install': True
}
