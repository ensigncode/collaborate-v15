# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockLocation(models.Model):
    _inherit = "stock.location"

    is_subcontract = fields.Boolean(string="Is Subcontract")

class StockMove(models.Model):
    _inherit = "stock.move"

    subcontract_avail_qty = fields.Float(string="Subcontract Available Quantity")
    subcontract_need_qty = fields.Float(string="Subcontract Need Quantity")
    intial_demand_qty = fields.Float(string="Intial Demand Qty")

    @api.model
    def create(self,vals):
        res = super(StockMove,self).create(vals)
        res.intial_demand_qty = res.product_uom_qty
        return res

    def write(self,vals):
        res = super(StockMove,self).write(vals)
        if 'update_move_product_uom' in self._context:
            return res
        if 'update_product_uom_qty' in self._context:
            return res
        if 'product_uom_qty' in vals and 'update_move_product_uom' not in self._context:
            for move in self:
                move.intial_demand_qty = move.product_uom_qty
        return res

class StockPicking(models.Model):
    _inherit = "stock.picking"    

    def update_move_demand_qty(self):
        location_ids = self.env['stock.location'].search([('is_subcontract','=',True)])
        if self.picking_type_id.check_existing_stock and location_ids:
            for move in self.move_ids_without_package:
                domain = [
                    ('product_id','=',move.product_id.id),
                    ('location_id','in',location_ids.ids),
                ]
                quant_ids = self.env['stock.quant'].search(domain)
                get_loc_dest_qty = 0
                if quant_ids:
                    get_loc_dest_qty = sum(quant.quantity for quant in quant_ids)
                product_uom_qty = move.intial_demand_qty
                remaining_qty = 0
                if get_loc_dest_qty > product_uom_qty:
                    remaining_qty = 0
                elif get_loc_dest_qty < product_uom_qty:
                    remaining_qty = product_uom_qty - get_loc_dest_qty
                # print('\n========remaining_qty==',remaining_qty)
                # print('=======get_loc_dest_qty==',get_loc_dest_qty)
                # print('\n========intial_demand_qty==',product_uom_qty)
                move.with_context(update_move_product_uom=1).write({'subcontract_avail_qty':get_loc_dest_qty,'product_uom_qty':remaining_qty})
        return True