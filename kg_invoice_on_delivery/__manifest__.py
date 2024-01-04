# -*- coding: utf-8 -*-


# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/


{
    'name': "Invoice on Delivery",

    'summary': """
        Option for invoice generation from delivery""",

    'description': """
        Option for invoice generation from delivery
    """,

    'author': "Klystron Global",
    'maintainer': "MINI K",
    'website': "www.klystronglobal.com",

    'category': 'Accounting',
    'version': '15.0.0.0.0',
    'license': 'AGPL-3',

    'depends': ['base','stock','sale','sale_stock'],
    'images': ["static/description/banner.png"],

    'data': [
        'views/validate.xml',
    ],
}
