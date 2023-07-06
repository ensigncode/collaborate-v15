# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Web Product Scanner',
    'version': '15.0.1.0.0',
    'category': 'Product',
    'sequence': 110,
    'description': """
        Scan Product Barcode to chek price from the website.
        
    """,
    'depends': ['barcodes', 'website'],
    'data': [
        'views/website_menu.xml',
        'views/barcode_templates.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_frontend': [
            'web_product_scanner/static/src/**/*',
        ],
    },
}
