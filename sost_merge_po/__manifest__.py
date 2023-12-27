# -*- coding: utf-8 -*-
{
    "name": "Sost. Merge PO",
    "category": "Purchase",
    "summary": "Sost. Merge PO",
    "description": '''
            Sost. Merge PO
        ''',
    "version": "15.0.2.0.0",
    "license": "LGPL-3",
    "depends": [
                "purchase",
                "purchase_stock",
                "sost_origin_so",
        ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/merge_po_line_views.xml",
        "views/purchase_order_views.xml",
    ],
    "author": "Parth Patel",
    "installable": True,
}
