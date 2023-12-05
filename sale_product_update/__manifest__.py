# -*- coding: utf-8 -*-
{
    "name": "Order Update Product",
    "category": "order",
    "summary": "Order Update Product",
    "description": '''
                Update Product in Order, 
                and in associated Transfers
            ''',
    "version": "15.0.3.0.0",
    "license": "LGPL-3",
    "depends": [
            'sale',
            'sale_management',
            'sale_stock',
        ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/update_product_views.xml",
        "views/res_users_views.xml",
        "views/product_category_views.xml",
        "views/stock_picking_views.xml",
    ],
    "author": "Parth Patel",
    "installable": True,
}