# -*- coding: utf-8 -*-

{
    'name': 'POS Validation Extend',
    'version': '15.0.1.0.0',
    'category': 'Point Of Sale',
    'description': """
        Removed address validation
    """,
    'depends': ['pos_coupon', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_validation_extend/static/src/js/payment_screen.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
