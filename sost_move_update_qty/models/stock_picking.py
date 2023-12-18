# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockLocation(models.Model):
    _inherit = "stock.location"

    is_subcontract = fields.Boolean(string="Is Subcontract")

    def update_parent_location(self):
        main_destination_id = self
        if main_destination_id:
            count = 0
            while count == 0:
                if main_destination_id.location_id and main_destination_id.location_id.usage == 'internal':
                    main_destination_id = main_destination_id.location_id
                    main_destination_id.is_subcontract = self.is_subcontract
                else:
                    count = 1
        return main_destination_id


    def write(self,vals):
        res = super(StockLocation,self).write(vals)
        if 'is_subcontract' in vals:
            self.update_parent_location()
        return res

    @api.model
    def create(self,vals):
        res = super(StockLocation,self).create(vals)
        res.update_parent_location()
        return res

class StockMove(models.Model):
    _inherit = "stock.move"

    subcontract_avail_qty = fields.Float(string="Subcontract Available Quantity")
    subcontract_need_qty = fields.Float(string="Subcontract Need Quantity")
    intial_demand_qty = fields.Float(string="Intial Demand Qty")
    qty_available = fields.Float(string="Qty Available")

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
        if location_ids:
            for move in self.move_ids_without_package:
                domain = [
                    ('product_id','=',move.product_id.id),
                    ('location_id','in',location_ids.ids),
                ]
                quant_ids = self.env['stock.quant'].search(domain)
                get_loc_dest_qty = 0
                if quant_ids:
                    get_loc_dest_qty = sum(quant.available_quantity for quant in quant_ids)
                product_uom_qty = move.intial_demand_qty
                remaining_qty = 0
                if get_loc_dest_qty > product_uom_qty:
                    remaining_qty = 0
                elif get_loc_dest_qty < product_uom_qty:
                    remaining_qty = product_uom_qty - get_loc_dest_qty
                if move.move_line_ids:
                    move.move_line_ids[0].qty_done = remaining_qty
                if len(move.move_line_ids) > 1:
                    for line in move.move_line_ids:
                        line.qty_done = 0
                # print('===v===========remaining_qty--',remaining_qty)
                move.with_context(update_move_product_uom=1).write({'qty_available':get_loc_dest_qty,'subcontract_avail_qty':get_loc_dest_qty,'product_uom_qty':remaining_qty})
        return True
