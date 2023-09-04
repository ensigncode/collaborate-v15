# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Export Images",
    "summary": "",
    "version": "15.0.0.1",
    "category": "Product",
    "website": "https://upstackers.com/",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product",
        "stock",
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/export_images_views.xml",
        "wizard/import_images_views.xml",
        'views/template_js.xml',
    ],
    'qweb': [
        "static/src/xml/template.xml",
    ],
}
