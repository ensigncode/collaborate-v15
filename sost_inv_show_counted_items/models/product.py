# -*- coding: utf-8 -*-

from odoo import _, models,fields

class Product(models.Model):
    _inherit = "product.product"

    def name_get(self):
        if 'transfer_product' in  self.env.context and 'default_location_dest_id' in self.env.context:
            location_dest_id = self.env['stock.location'].browse(int(self.env.context['default_location_dest_id']))
            picking_type_id = self.env['stock.picking.type'].browse(int(self.env.context['default_picking_type_id']))
            if picking_type_id.show_stock:
                result = super().name_get()
                final_result = []
                for res in result:
                    quant_ids = self.env['stock.quant'].search([('product_id','=',res[0]),('location_id','=',location_dest_id.id)])
                    available_qty = sum(quant.available_quantity for quant in quant_ids)
                    final_result.append((res[0], res[1] + ' (%s)' % str(available_qty).split('.')[0]))
                return final_result
            else:
                return super().name_get()
        return super().name_get()

