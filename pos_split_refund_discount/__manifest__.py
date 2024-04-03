# -*- coding: utf-8 -*-

{
    'name': 'POS Refund Discount Split',
    'version': '15.0.1.0.1',
    'category': 'Point Of Sale',
    'description': """
        Add ability to split discount in refunds as well
    """,
    'depends': ['pos_coupon', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_split_refund_discount/static/src/js/models.js',
            'pos_split_refund_discount/static/src/js/TicketScreen.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
