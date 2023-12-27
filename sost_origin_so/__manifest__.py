# -*- coding: utf-8 -*-
{
    "name": "MRP Sale",
    "category": "MRP",
    "summary": "MRP Sale",
    "description": '''
            Passing the Order reference in Manufacturing Order
        ''',
    "version": "15.0.2.0.0",
    "license": "LGPL-3",
    "depends": [
                "mrp",
                "sale_management",
                "sale_stock",
                "purchase_stock",
        ],
    "data": [
        "views/mrp_production_views.xml",
        "views/purchase_order_views.xml",
    ],
    "author": "Parth Patel",
    "installable": True,
}
