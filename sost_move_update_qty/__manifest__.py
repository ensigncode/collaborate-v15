# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sost. Move Update Demand Qty',
    'version' : '15.0.0.0.8',
    'summary': 'Sost. Move Update Demand Qty',
    'sequence': 10,
    'description': """
        Sost. Move Update Demand Qty
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
