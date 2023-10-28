# -*- coding: utf-8 -*-
{
    'name': "POS Apply Multiple Coupon",
    'description': """
        POS Apply Multiple Coupon
    """,
    'category': 'Point Of Sale',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale','pos_coupon'],

    'data': [
        # Security
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
