# -*- coding: utf-8 -*-
{
    "name": "Transfer Update Product",
    "category": "Transfers",
    "summary": "Transfer Update Product",
    "description": '''
                Update Product in Transfers, 
                and in associated Orders
            ''',
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
            'sale',
            'sale_management',
            'sale_stock',
        ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/transfer_handling_unit_views.xml",
        "views/product_category_views.xml",
        "views/stock_picking_type_views.xml",
    ],
    "author": "Parth Patel",
    "installable": True,
}