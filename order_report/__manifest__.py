# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Order Reports',
    'version': '15.0.0.0',
    'category': 'custom',
    'summary': 'Order Reports',
    'description': """
        Order Reports
    """,
    'depends': [
                'purchase_stock',
                'sale_stock',
                'sale_purchase_stock',
            ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/order_report_view.xml',
        'views/sale_order_view.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
}
