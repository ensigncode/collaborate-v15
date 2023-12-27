# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"

    def update_demand_qty(self):
        if self.picking_id.picking_type_id.check_existing_stock and self.picking_id.origin:
            location_dest_id = self.picking_id.location_dest_id
            domain = [
                ('product_id','=',self.product_id.id),
                ('location_id','=',location_dest_id.id),
                ('on_hand','=',True),
            ]
            quant_ids = self.env['stock.quant'].search(domain)
            get_loc_dest_qty = 0
            if quant_ids:
                get_loc_dest_qty = sum(quant.inventory_quantity_auto_apply for quant in quant_ids if quant.inventory_quantity_auto_apply > 0)
            
            product_uom_qty = self.product_uom_qty
            remaining_qty = 0
            if get_loc_dest_qty > product_uom_qty:
                remaining_qty = 0
            elif get_loc_dest_qty < product_uom_qty:
                remaining_qty = product_uom_qty - get_loc_dest_qty
            self.with_context(update_product_uom_qty=1).update({'product_uom_qty':remaining_qty})
        return True

    def write(self,vals):
        res = super(StockMove,self).write(vals)
        if 'update_product_uom_qty' in self._context and self._context['update_product_uom_qty']:
            return res
        if 'product_uom_qty' in vals:
            for move in self:
                move.update_demand_qty()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        results = super(StockMove, self).create(vals_list)
        for res in results:
            res.update_demand_qty()
        return results

    