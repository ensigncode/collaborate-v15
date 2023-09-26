# Copyright 2021 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Website Sale Customization",
    "summary": "Animation of add to cart and change position",
    "version": "14.0.1.0.0",
    "category": "Extra Tools",
    'author': 'EnsignCode Solutions',
    'company': 'EnsignCode Solutions',
    'maintainer': 'EnsignCode Solutions',
    'website': "https://www.ensigncode.com",
    "license": "LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
    "depends": ["website_sale","website_sale_wishlist","website_sale_comparison"],
    "data": [

        'views/template.xml',
    ],
}