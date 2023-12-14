# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    def write(self,vals):
        print('\n\n====write====StockMoveLine====+WRITEEE---',self._context)
        res = super(StockMoveLine,self).write(vals)
        if 'update_product_uom_qty' in self._context:
            return res
        # if 'product_uom_qty' in vals or ('state' in vals and vals['state'] in ('partially_available','assigned')):
        #     for move in self:
        #         move.update_demand_qty()
        return res

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
            print('\n===quant_ids==',quant_ids)
            get_loc_dest_qty = 0
            if quant_ids:
                get_loc_dest_qty = sum(quant.inventory_quantity_auto_apply for quant in quant_ids if quant.inventory_quantity_auto_apply > 0)
        return get_loc_dest_qty

    # def _action_assign(self, force_qty=False):
    #     print('\n\n==========_action_assign============')
    #     """ Reserve stock moves by creating their stock move lines. A stock move is
    #     considered reserved once the sum of `reserved_qty` for all its move lines is
    #     equal to its `product_qty`. If it is less, the stock move is considered
    #     partially available.
    #     """
    #     res = super(StockMove,self)._action_assign()
    #     for move in self:
    #         move.with_context(update_demand_qty=1).update_demand_qty()
    #         # if move.purchase_line_id and  move.purchase_line_id.product_qty:
    #         #     product_uom_qty = move.purchase_line_id.product_qty
    #         #     # product_uom_qty = move.purchase_line_id.product_qty
    #         #     get_loc_dest_qty = move.get_loc_dest_qty()
    #         #     print('\n\n==SWADWADW==get_loc_dest_qty==',get_loc_dest_qty)
    #         #     remaining_qty = 0
    #         #     if get_loc_dest_qty > product_uom_qty:
    #         #         remaining_qty = 0
    #         #     elif get_loc_dest_qty < product_uom_qty:
    #         #         remaining_qty = product_uom_qty - get_loc_dest_qty
    #         #     print('\n\n=------remaining_qty--',remaining_qty)
    #     return res


    def update_demand_qty(self):
        print('\n\n\n========update_demand_qty==',self)
        # stop
        print('=======self.picking_id==',self.picking_id)
        print('=======self.picking_id.picking_type_id.check_existing_stock==',self.picking_id.picking_type_id.check_existing_stock)
        print('========self.picking_id.origin==',self.picking_id.origin)
        if self.picking_id.picking_type_id.check_existing_stock and self.picking_id.origin:
            location_dest_id = self.picking_id.location_dest_id
            domain = [
                ('product_id','=',self.product_id.id),
                ('location_id','=',location_dest_id.id),
                # ('on_hand','=',True),
            ]
            quant_ids = self.env['stock.quant'].search(domain)
            print('====quant_ids==',quant_ids)

            for quant in quant_ids:
                print('=-----quant.quantity--',quant.quantity)

            get_loc_dest_qty = 0
            if quant_ids:
                get_loc_dest_qty = sum(quant.quantity for quant in quant_ids)
                print('=-----get_loc_dest_qty--',get_loc_dest_qty)
                
            
            if self.purchase_line_id.product_uom_qty:
                product_uom_qty = self.purchase_line_id.product_uom_qty
            else:
                product_uom_qty = self.product_uom_qty


            remaining_qty = 0
            if get_loc_dest_qty > product_uom_qty:
                remaining_qty = 0
            elif get_loc_dest_qty < product_uom_qty:
                remaining_qty = product_uom_qty - get_loc_dest_qty


            if quant_ids:
                print('=-----get_loc_dest_qty--',get_loc_dest_qty)
                print('=-----product_uom_qty--',product_uom_qty)
                print('=-----self--',self,self.picking_id)
                print('=-----remaining_qty--',remaining_qty)
                # stop
            self.with_context(update_product_uom_qty=1).product_uom_qty = remaining_qty
            # self.with_context(update_product_uom_qty=1).write({'product_uom_qty':remaining_qty})
        return True

    def write(self,vals):
        res = super(StockMove,self).write(vals)
        print('\n\n====write====StockMove====+WRITEEE---',vals,self)
        
        if 'update_demand_qty' in self._context:
            print('==========UPDATE DEMAND QTY================')
            return res

        if 'update_product_uom_qty' in self._context:
            print('====================================')
            return res
        if 'product_uom_qty' in vals or ('state' in vals and vals['state'] in ('assigned','confirmed','waiting','partially_available')):
            print('===============SSSSSSSSSSSS=====================',self)
            
            for move in self:
                print('===============1111=====================')

                move.update_demand_qty()
                print('===============22222=====================')

        return res

class StockPicking(models.Model):
    _inherit = "stock.picking"    

    def update_demand_qty(self):
        print('\n\n====PICKINg========+update_demand_qty---')
        for move in self.move_ids_without_package:
            move.update_demand_qty()
        return True


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