# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    active = fields.Boolean(string="Active",copy=False,default=True)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sequence = fields.Integer(string="Sequence",default=10)
