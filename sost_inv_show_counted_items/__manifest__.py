# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Inv Show Counted Items',
    'version': '15.1.0.1',
    'category': '',
    'summary': '',
    'description': """
            Inventory, Show Counted Items
    """,
    'depends': [
            'sale',
            'sale_stock',
            ],
    'data': [
        'views/stock_picking.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'assets': {
    },
    'license': 'LGPL-3',
}
