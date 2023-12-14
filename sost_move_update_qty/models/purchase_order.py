# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_product_exiting_stock(self):
        for line in self.order_line.filtered(lambda x:x.check_product_stock):
            line.update_remaining_qty()
        return True

    def apply_product_qty(self):
        for line in self.order_line.filtered(lambda x:x.check_product_stock):
            line.product_qty = line.check_product_qty
        return True

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    check_product_stock = fields.Boolean(string="Check Product Stock",copy=False)
    check_product_qty = fields.Float(string="Check Product Qty")

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        for line in self:
            if 'update_product_uom_qty' not in self._context:
                line.check_product_qty = line.product_qty


    def update_remaining_qty(self):
        print('\n\n\n========update_demand_qty==',self.order_id.picking_type_id.check_existing_stock)
        if self.order_id.picking_type_id.check_existing_stock:
            print('\n\n\n========update_demand_qty==',self)
            location_dest_id = self.order_id.picking_type_id.default_location_dest_id
            print('\n\n\n========location_dest_id==',location_dest_id)
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

                
            product_uom_qty = self.product_uom_qty
            # product_uom_qty = self.check_product_qty
            remaining_qty = 0
            if get_loc_dest_qty > product_uom_qty:
                remaining_qty = 0
            elif get_loc_dest_qty < product_uom_qty:
                remaining_qty = product_uom_qty - get_loc_dest_qty
            print('=-----remaining_qty--',remaining_qty)
            self.with_context(update_product_uom_qty=1).check_product_qty = remaining_qty
        return True

    # def write(self,vals):
    #     res = super(PurchaseOrderLine,self).write(vals)
    #     if 'update_product_uom_qty' in self._context:
    #         return res
    #     if 'product_qty' in vals or 'product_uom_qty' in vals:
    #         for line in self:
    #             line.update_remaining_qty()
    #     return res


    # @api.model_create_multi
    # def create(self,vals):
    #     res = super(PurchaseOrderLine,self).create(vals)
    #     for line in res:
    #         line.update_remaining_qty()
    #     return res

