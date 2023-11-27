# -*- coding: utf-8 -*-

from odoo import models,fields,_,api

class StockMove(models.Model):
    _inherit = "stock.move"

    def get_is_production(self):
        ctx = self._context
        is_production = False
        if 'params' in ctx and ctx['params'] and 'model' in ctx['params'] and ctx['params']['model'] == 'mrp.production':
            is_production = True 
        return is_production

    is_production = fields.Boolean(string="Is Production",default=lambda x:x.get_is_production())
    consider_qty = fields.Float(string="Consider Qty")

    @api.depends('product_id', 'product_uom', 'product_uom_qty','is_production','raw_material_production_id.qty_producing','raw_material_production_id.product_qty')
    def _compute_product_qty(self):
        for move in self:
            move.product_qty  = 1
            if move.is_production and move.raw_material_production_id:
                final_product_qty = 0
                if move.raw_material_production_id.state == 'done':
                    product_qty = move.raw_material_production_id.product_qty 
                else:
                    product_qty = move.raw_material_production_id.qty_producing
                if product_qty > 0:
                    product_uom_qty = (move.product_uom_qty * move.raw_material_production_id.qty_producing) / move.raw_material_production_id.product_qty 
                    final_product_qty = move.product_uom._compute_quantity(
                        product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
                move.product_qty = final_product_qty
            else:
                move.product_qty = move.product_uom._compute_quantity(
                    move.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')