# -*- coding: utf-8 -*-
{
    'name': "POS Apply Multiple Coupon",
    'description': """
        POS Apply Multiple Coupon
    """,
    'category': 'Point Of Sale',
    'version': '15.0.1.0.1',

    'depends': ['multi_promotion_coupons_lensa'],

    'data': [
    ],
    'assets': {
        'point_of_sale.assets': [
            'multi_promotion_coupons_custom/static/src/js/multi_promotion_sale_management_screen.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
