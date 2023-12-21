# -*- coding: utf-8 -*-

from odoo import _, models,fields

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    show_stock = fields.Boolean(string="Show Stock")
