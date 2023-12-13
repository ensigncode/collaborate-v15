# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    check_existing_stock = fields.Boolean(string="Check Existing Stock")
    
class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        print('\n\nn=======Pickings---',self.picking_ids)
        for picking in self.picking_ids:
            move_ids = picking.move_ids_without_package
            for move in picking.move_ids_without_package:
                move.update_demand_qty()
        return res

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    # def button_confirm(self):
    #     res = super(PurchaseOrder,self).button_confirm()
    #     print('\n\nn=======Pickings---',self.picking_ids)
    #     for picking in self.picking_ids:
    #         move_ids = picking.move_ids_without_package
    #         print('==========move_ids---',move_ids)
    #         for move in picking.move_ids_without_package:
    #             move.update_demand_qty()
    #     return res




    # check_existing_stock = fields.Boolean(string="Check Existing Stock")
    