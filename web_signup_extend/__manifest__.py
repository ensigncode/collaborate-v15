# -*- coding: utf-8 -*-
{
    'name': "Signup With Newsletter & SMS",

    'summary': """
        Module will add newsletter and terms checkboxes on signup page
    """,

    'category': 'web',
    'version': '15.0.1.0.0',

    'depends': ['base', 'auth_signup'],

    'data': [
        'views/auth_oauth_templates.xml',
        'views/partner_views.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'web_signup_extend/static/**/*',
        ],
    },
}
