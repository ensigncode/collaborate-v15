# -*- coding: utf-8 -*-
{
    'name': "Signup With Newsletter & SMS",

    'summary': """
        Module will add newsletter and terms checkboxes on signup page
    """,

    'category': 'web',
    'version': '15.0.1.1.1',

    'depends': ['base', 'auth_signup', 'portal', 'website'],

    'data': [
        'views/auth_oauth_templates.xml',
        'views/partner_views.xml',
        'views/customer_portal.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'web_signup_extend/static/**/*',
        ],
    },
}
