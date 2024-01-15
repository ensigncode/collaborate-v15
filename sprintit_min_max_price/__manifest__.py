# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################
{
    'name': 'Min-Max Prices on Sales Order',
    'version': '14.0',
    'website': 'https://www.sprintit.fi',
    'category': 'Sales',
    'summary': 'Min-Max Price on Sale Order',
    'author': 'SprintIT',
    'maintainer': 'SprintIT',
    'website': 'https://sprintit.fi/in-english',
    'description': """
Min-Max Price on Sales Order
===============================
* Min-Max Price Configuration to get Product price from pricelist accordingly.
* Standard Odoo uses the first one found.
""",
    'depends': [
        'sale_management',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'images': ['static/description/cover.jpg', ],
    "external_dependencies": {},
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'price': 0.0,
    'currency': 'EUR',
}
