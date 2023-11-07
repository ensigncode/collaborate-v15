# -*- coding: utf-8 -*-
{
    "name": "Manage Customer Products",
    "category": "product",
    "summary": "Manage Customer Products",
    "version": "14.0.0.0.1",
    "license": "LGPL-3",
    "depends": [
        'product',
        'purchase',
        'sale_stock',
        'sale_management',
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "views/repair_request_views.xml",
        "views/repair_image_views.xml",
    ],
    'qweb': ['static/src/xml/*.xml'],
    "author": "Sostenia",
    "installable": True,
}