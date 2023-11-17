# -*- coding: utf-8 -*-

from odoo import models,fields,api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    move_line_ids_without_package = fields.One2many('stock.move.line', 'picking_id', 'Operations without package', domain=[('is_cos_category','=',False),'|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)])

    def update_hu_lines(self):

        picking_ids = False
        sale_id = False
        if self.sale_id:
            sale_id = self.sale_id
            picking_ids = self.sale_id.picking_ids
        elif self.origin:
            picking_ids = self.env['stock.picking'].search([('origin','=',self.origin)])
            sale_id = self.env['sale.order'].search([('name','=',self.origin)])
        if not picking_ids:
            picking_ids = self
        update_move = False
        moves = self.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.is_cos_category)
        if moves:
            update_move = moves[-1]
            update_move.product_uom_qty = 0

        if update_move:
            for picking in picking_ids:
                lines =  picking.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.is_cos_category)
                moves = picking.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.is_cos_category)
                if moves:
                    if len(moves) > 1:
                        extra_moves = moves[0:len(moves)-1]
                        for move in extra_moves:
                            query1 = "DELETE FROM stock_move_line WHERE move_id = %s" %(move.id)
                            self.env.cr.execute(query1)
                            query2 = "DELETE FROM stock_move WHERE id = %s" %(move.id)
                            self.env.cr.execute(query2)
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
                if len(picking_ids) > 1 and self.id != picking.id and update_move:
                    query = """
                            INSERT INTO stock_move(PRODUCT_ID,NAME,DATE,COMPANY_ID,PICKING_ID,PRODUCT_UOM_QTY,PRODUCT_UOM,LOCATION_ID,LOCATION_DEST_ID,PROCURE_METHOD)
                            VALUES (%s,'%s','%s',%s,'%s','%s','%s','%s','%s','%s')
                    """ %(update_move.product_id.id,update_move.product_id.display_name,update_move.picking_id.date.strftime('%Y-%m-%d %H:%M:%S'),update_move.picking_id.company_id.id,picking.id,'0',update_move.product_id.uom_id.id,update_move.picking_id.location_id.id,update_move.picking_id.location_dest_id.id,'make_to_stock')
                    self.env.cr.execute(query)
        return True

    def write(self,vals):
        res = super(StockPicking,self).write(vals)
        for picking in self:
            if picking.move_ids_without_package:
                picking.update_hu_lines()
        return res

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    categ_id = fields.Many2one('product.category',related="product_id.categ_id",store=True)
    is_cos_category = fields.Boolean(string="Is COS Product",related="categ_id.is_cos_category",store=True)


    @api.model_create_multi
    def create(self, vals_list):
        moves = super(StockMoveLine,self).create(vals_list)
        for move in moves:
            if move.move_id.picking_id:
                move.move_id.picking_id.update_hu_lines()
        return moves
