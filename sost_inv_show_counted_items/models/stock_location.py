# -*- coding: utf-8 -*-

from odoo import _, models,fields

class StockLocation(models.Model):
    _inherit = "stock.location"

    def name_get(self):
        if 'transfer_product' in  self.env.context and 'default_product_id' in self.env.context:
            product_id = self.env['product.product'].browse(int(self.env.context['default_product_id']))
            picking_type_id = self.env['stock.picking.type'].browse(int(self.env.context['default_picking_type_id']))
            if picking_type_id.show_stock:
                result = super().name_get()
                final_result = []
                for res in result:
                    quant_ids = self.env['stock.quant'].search([('product_id','=',int(product_id)),('location_id','=',res[0]),('on_hand','=',True)])
                    available_qty = sum(quant.available_quantity for quant in quant_ids)
                    final_result.append((res[0], res[1] + ' (%s)' % str(available_qty).split('.')[0]))
                return final_result
            else:
                return super().name_get()
        return super().name_get()

