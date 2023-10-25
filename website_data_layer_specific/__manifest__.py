# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Ecommerce Data Layer Specification',
    'version': '15.0.1.0.0',
    'category': 'Ecommerce',
    'sequence': 216,
    'description': """
        Ecommerce data layer specifications
    """,
    'depends': ['website_sale', 'base'],
    'data': [
        'views/website_sale.xml',
        'views/website_sale_templates.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_frontend': [
            'website_data_layer_specific/static/src/js/website_sale.js',
            'website_data_layer_specific/static/src/js/website_sale_validate.js'
        ],
    },
}
