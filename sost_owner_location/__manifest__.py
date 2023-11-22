# -*- coding: utf-8 -*-
{
    'name': "Sost Owner Location",
    'description': """
        Sost Owner Location
    """,
    'category': 'Inventory',
    'version': '15.0.1.0.0',

    'depends': [
                'stock',
                'contacts',
        ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': True
}
