# -*- coding: utf-8 -*-
{
    "name": "MRP Raport Consum",
    "category": "MRP",
    "summary": "MRP Raport Consum",
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
            "mrp",
            "mrp_account_enterprise",
            ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "wizard/mrp_consume_views.xml",
    ],
    "author": "Parth Patel",
    "installable": True,
}
