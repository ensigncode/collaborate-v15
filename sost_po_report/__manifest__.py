# -- coding: utf-8 --
{
    "name": "SOST PO REPORT",
    "summary": "Purchase Report",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "category": "purchase",
    "depends": [
                "base", 
                "purchase",
                'purchase_stock',
                'account'
            ],
    "data": [
        'report/po_report_external_layout.xml',
        'report/po_report_template.xml',
        'report/report_action.xml',
        'views/purchase_order_view.xml',
    ],
    "auto_install": False,
    "installable": True,
}
