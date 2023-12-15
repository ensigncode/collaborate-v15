# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    check_existing_stock = fields.Boolean(string="Check Existing Stock")
    
# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     def action_confirm(self):
#         res = super(SaleOrder,self).action_confirm()
#         for picking in self.picking_ids:
#             move_ids = picking.move_ids_without_package
#             for move in picking.move_ids_without_package:
#                 move.update_demand_qty()
#         return res
