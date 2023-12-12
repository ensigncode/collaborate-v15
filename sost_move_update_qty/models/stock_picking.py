# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"

    def get_loc_dest_qty(self):
        get_loc_dest_qty = 0
        if self.picking_id.picking_type_id.check_existing_stock and self.picking_id.origin:
            location_dest_id = self.picking_id.location_dest_id
            domain = [
                ('product_id','=',self.product_id.id),
                ('location_id','=',location_dest_id.id),
                ('on_hand','=',True),
            ]
            quant_ids = self.env['stock.quant'].search(domain)

            print('====quant_ids==',quant_ids)
            get_loc_dest_qty = 0
            if quant_ids:
                get_loc_dest_qty = sum(quant.inventory_quantity_auto_apply for quant in quant_ids if quant.inventory_quantity_auto_apply > 0)
        return get_loc_dest_qty


    def _action_assign(self, force_qty=False):
        print('\n\n\n=========_action_assign==========')
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `reserved_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        res = super(StockMove,self)._action_assign()
        for move in self:

            if move.purchase_line_id and  move.purchase_line_id.product_qty:
                product_uom_qty = move.purchase_line_id.product_qty
                # product_uom_qty = move.purchase_line_id.product_qty
                get_loc_dest_qty = move.get_loc_dest_qty()
                print('\n\n==SWADWADW==get_loc_dest_qty==',get_loc_dest_qty)
                remaining_qty = 0
                if get_loc_dest_qty > product_uom_qty:
                    remaining_qty = 0
                elif get_loc_dest_qty < product_uom_qty:
                    remaining_qty = product_uom_qty - get_loc_dest_qty
                print('\n\n=------remaining_qty--',remaining_qty)
                # move.with_context(update_product_uom_qty=1).write({'product_uom_qty':remaining_qty})
        return res



    def update_demand_qty(self):

        print('\n\n\n========update_demand_qty==')
        print('=======self.picking_id==',self.picking_id)
        print('=======self.picking_id.picking_type_id.check_existing_stock==',self.picking_id.picking_type_id.check_existing_stock)
        print('========self.picking_id.origin==',self.picking_id.origin)

        if self.picking_id.picking_type_id.check_existing_stock and self.picking_id.origin:
            location_dest_id = self.picking_id.location_dest_id
            domain = [
                ('product_id','=',self.product_id.id),
                ('location_id','=',location_dest_id.id),
                ('on_hand','=',True),
            ]
            quant_ids = self.env['stock.quant'].search(domain)

            print('====quant_ids==',quant_ids)
            get_loc_dest_qty = 0
            if quant_ids:
                get_loc_dest_qty = sum(quant.inventory_quantity_auto_apply for quant in quant_ids if quant.inventory_quantity_auto_apply > 0)
            

            if self.purchase_line_id.product_uom_qty:
                product_uom_qty = self.purchase_line_id.product_uom_qty
            else:
                product_uom_qty = self.product_uom_qty
                
            print('-====get_loc_dest_qty=product_uom_qty=',get_loc_dest_qty,self.product_uom_qty)

            remaining_qty = 0
            if get_loc_dest_qty > product_uom_qty:
                remaining_qty = 0
            elif get_loc_dest_qty < product_uom_qty:
                remaining_qty = product_uom_qty - get_loc_dest_qty
            print('\n\n=------remaining_qty--',remaining_qty)
            self.with_context(update_product_uom_qty=1).update({'product_uom_qty':remaining_qty})
        return True

    def write(self,vals):
        res = super(StockMove,self).write(vals)
        print('\n====self._context==',vals)
        if 'update_product_uom_qty' in self._context:
            return res
        if 'product_uom_qty' in vals or ('state' in vals and vals['state'] in ('partially_available','assigned')):
            for move in self:
                move.update_demand_qty()
        return res

    # @api.model_create_multi
    # def create(self, vals_list):
    #     results = super(StockMove, self).create(vals_list)
    #     for res in results:
    #         res.update_demand_qty()
    #     return results

# class StockPicking(models.Model):
#     _inherit = "stock.picking"      

    # def action_assign(self):
    #     """ Reserve stock moves by creating their stock move lines. A stock move is
    #     considered reserved once the sum of `reserved_qty` for all its move lines is
    #     equal to its `product_qty`. If it is less, the stock move is considered
    #     partially available.
    #     """
 
    #     print('\n\n\n======ACTION====action_assign=========')
    #     res = super(StockPicking,self).action_assign()
    #     if self.picking_type_id.check_existing_stock and self.origin:
    #         for move in self.move_ids_without_package:
    #             get_loc_dest_qty = move.get_loc_dest_qty()
    #             print('\n\n===get_loc_dest_qty==',get_loc_dest_qty)
    #             product_uom_qty =  self.product_uom_qty
                
    #             if move.purchase_line_id and  move.purchase_line_id.product_qty:
    #                 product_uom_qty = move.purchase_line_id.product_qty
                
    #             if move.sale_line_id and move.sale_line_id.product_qty:
    #                 product_uom_qty = move.sale_line_id.product_qty
    #                 get_loc_dest_qty = move.get_loc_dest_qty()


    #             remaining_qty = 0
    #             if get_loc_dest_qty > product_uom_qty:
    #                 remaining_qty = 0
    #             elif get_loc_dest_qty < product_uom_qty:
    #                 remaining_qty = product_uom_qty - get_loc_dest_qty
    #             move.with_context(update_product_uom_qty=1).write({'product_uom_qty':remaining_qty})

    #     return res