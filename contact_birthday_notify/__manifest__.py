# -*- coding: utf-8 -*-
{
    'name': "Contact Birthday Notification",
    'summary': """
        Contact Birthday Notification
    """,
    'category': 'contact',
    'version': '15.0.1.1.1',
    'depends': [
            'base',
            'sale',
            'sale_management',
            'sale_coupon',
        ],
    'data': [
        'data/ir_cron.xml',
        'data/template.xml',
        'views/res_partner_views.xml',
    ],
    'assets': {},
}
