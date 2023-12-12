# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Move Update Demand Qty',
    'version' : '15.0.0.0.1',
    'summary': 'Move Update Demand Qty',
    'sequence': 10,
    'description': """
        Move Update Demand Qty
    """,
    'category': 'Stock',
    'images' : [],
    'depends' : [
                'stock',
                'sale_management',

            ],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
}
