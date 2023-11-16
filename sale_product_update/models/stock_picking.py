# -*- coding: utf-8 -*-

from odoo import models,fields,api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def update_hu_lines(self):
        lines =  self.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.is_cos_category)
        moves = self.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.is_cos_category)
        if moves:
            update_move = moves[-1]
            update_move.product_uom_qty = 0
            if len(moves) > 1:
                extra_moves = moves[0:len(moves)-1]
                for move in extra_moves:
                    query1 = "DELETE FROM stock_move_line WHERE move_id = %s" %(move.id)
                    self.env.cr.execute(query1)

                    query2 = "DELETE FROM stock_move WHERE id = %s" %(move.id)
                    self.env.cr.execute(query2)

            if self.sale_id:
                sale_id = self.sale_id
            else:
                sale_id = self.env['sale.order'].search([('name','=',self.origin)])
            if sale_id:
                order_line = sale_id.order_line.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.is_cos_category)
                for line in order_line:
                    query = "DELETE FROM sale_order_line WHERE id = %s" %(line.id)
                    self.env.cr.execute(query)
               
                query = """
                        INSERT INTO sale_order_line(PRODUCT_ID,PRODUCT_UOM_QTY,PRICE_UNIT,ORDER_ID,NAME,CUSTOMER_LEAD,PRODUCT_UOM,SEQUENCE)
                        VALUES (%s,'%s',%s,%s,'%s','%s','%s','%s')
                """ %(update_move.product_id.id,'0','0',sale_id.id,update_move.product_id.display_name,'0',update_move.product_id.uom_id.id,'11')
                self.env.cr.execute(query)
        return True

    def write(self,vals):
        res = super(StockPicking,self).write(vals)
        if 'move_ids_without_package' in vals and vals['move_ids_without_package']:
            for picking in self:
                if picking.move_ids_without_package:
                    picking.update_hu_lines()
        return res