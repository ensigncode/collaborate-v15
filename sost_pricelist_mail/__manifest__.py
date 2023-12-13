# -*- coding: utf-8 -*-
{
    "name": "Sost. Product Pricelist",
    "category": "product",
    "summary": "Sost. Product Pricelist",
    "version": "16.0.0.0.1",
    "license": "LGPL-3",
    "depends": [
        'product',
        'sale_management',
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_pricelist_template.xml",
        "data/mail_template.xml",
        "wizard/update_pricelist_views.xml",
        "wizard/mail_compose_message_views.xml",
        "views/product_pricelist_views.xml",
    ],
    'qweb': [],
    "author": "Sostenia",
    "installable": True,
}
