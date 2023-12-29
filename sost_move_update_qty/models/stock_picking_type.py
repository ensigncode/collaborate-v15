# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    check_existing_stock = fields.Boolean(string="Check Existing Stock")
