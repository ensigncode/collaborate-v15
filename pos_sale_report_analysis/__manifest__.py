# -*- coding: utf-8 -*-

{
    'name': 'POS Sale Report Analysis',
    'version': '15.0.1.0.1',
    'category': 'Point Of Sale',
    'description': """
        Add ability to notify shipment of product when it's done.
    """,
    'depends': ['pos_sale'],
    'data': [
        'views/sales_reporting_pivot_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
