# -*- coding: utf-8 -*-
{
    'name': "POS Apply Multiple Coupon",
    'description': """
        POS Apply Multiple Coupon
    """,
    'category': 'Point Of Sale',
    'version': '15.0.1.0.6',

    'depends': ['point_of_sale','pos_coupon', 'pos_sale'],

    'data': [
        # Security
        'security/ir.model.access.csv'
    ],
    'assets': {
        'point_of_sale.assets': [
            'multi_promotion_coupons_lensa/static/src/js/multi_promotion_sale_management_screen.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
