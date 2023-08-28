# -*- coding: utf-8 -*-

{
    'name': 'POS Shipment Notification',
    'version': '15.0.1.0.0',
    'category': 'Point Of Sale',
    'description': """
        Add ability to notify shipment of product when it's done.
    """,
    'depends': ['pos_coupon', 'point_of_sale','stock'],
    'data': [
        'data/mail_template_data.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
