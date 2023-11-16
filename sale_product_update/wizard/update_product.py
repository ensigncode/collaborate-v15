# -*- coding: utf-8 -*-

from odoo import models,fields,api
from datetime import datetime,date


class UpdateProductLine(models.TransientModel):
    _name = 'update.product.line'
    _description = 'Update Product line'
    _order = 'id desc'

    order_id = fields.Many2one('sale.order',string="Order")
    warehouse_id = fields.Many2one(related="order_id.warehouse_id",string="Warehouse",store=True)
    delivery_date = fields.Date(string="Delivery Date")
    sequence = fields.Integer(string="Sequence")
    partner_id = fields.Many2one('res.partner',string="Customer")
    product_code = fields.Char(string="Handling Unit")
    product_id = fields.Many2one('product.product',string="Product")
    update_product_id = fields.Many2one('update.product',string="Product")
    need_to_update = fields.Boolean(string="Needs To Update")

    @api.onchange('product_code')
    def _onchange_product_code(self):
        for obj in self:
            obj.need_to_update =  True

    '''
        Function to get the Product ID on the basis of product name.
    '''
    def get_product(self,product_code):
        product_id = False
        record = self
        if record.product_code:
            product_code = record.product_code
            product_id = self.env['product.product'].search([
                                '|',('barcode','ilike',product_code),
                                ('default_code','ilike',product_code)],limit=1)
            if not product_id:
                product_id = self.env['product.product'].search([('name','ilike',product_code)],limit=1)
        return product_id


class UpdateProduct(models.TransientModel):
    _name = 'update.product'
    _description = 'Update Product'
    _order = 'id desc'

    name = fields.Char(default="Handling Unit")
    update_product_ids = fields.One2many('update.product.line','update_product_id',string="Update Product")

    def get_product_code(self,order_id):
        categ_id = self.env['product.category'].search([('is_cos_category','=',True)],limit=1)
        product_code = ''
        order_line = order_id.order_line.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
        if order_line:
            product_code = order_line[-1].product_id.name
        return product_code


    def get_order_vals(self,order_id):
        delivery_date = False
        product_code  = ''
        if order_id and order_id.expected_date:
            delivery_date = order_id.expected_date.date()
        elif order_id and order_id.commitment_date:
            delivery_date = delivery_date.date()
        product_code = self.get_product_code(order_id)
        vals = {
            'partner_id':order_id.partner_id.id,
            'delivery_date':delivery_date,
            'order_id':order_id.id,
            'product_code':product_code,
        }
        return vals

    @api.model
    def default_get(self,vals):
        res = super(UpdateProduct,self).default_get(vals)
        order_ids = self.env['sale.order'].search([('state','=','sale')])
        warehouse_ids = self.env.user.order_warehouse_ids
        sequence = 10
        update_product = []
        for warehouse in warehouse_ids:
            sale_ids = order_ids.filtered(lambda x:x.warehouse_id and x.warehouse_id.id == warehouse.id)
            for order in sale_ids:
                if order.picking_ids.filtered(lambda x:x.state == 'assigned'):
                    vals = self.get_order_vals(order)
                    vals.update({'sequence':sequence})
                    update_product.append((0,0,vals))
                    sequence += 1
        res['update_product_ids'] = update_product
        return res

    '''
        Function to get the product name, and unlink the perious product- with the new product ID.  
    '''
    def action_confirm(self):
        categ_id = self.env['product.category'].search([('is_cos_category','=',True)],limit=1)
        if self.update_product_ids:
            for line in self.update_product_ids:
                line.need_to_update = False
                product_id = line.get_product(line.product_code)
                if line.product_code and categ_id and product_id:
                    company_id = self.env.company.id
                    uom_id = product_id.uom_id.id
                    product_name = product_id.display_name
                    product_id = product_id.id
                    order_line = line.order_id.order_line.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
                    if order_line:
                        for line in order_line:
                            query = "DELETE FROM sale_order_line WHERE id = %s" %(line.id)
                            self.env.cr.execute(query)
                    query = """
                            INSERT INTO sale_order_line(PRODUCT_ID,PRODUCT_UOM_QTY,PRICE_UNIT,ORDER_ID,NAME,CUSTOMER_LEAD,PRODUCT_UOM,SEQUENCE)
                            VALUES (%s,'%s',%s,%s,'%s','%s','%s','%s')
                    """ %(product_id,'0','0',line.order_id.id,product_name,'0',uom_id,'11')
                    self._cr.execute(query)
                    picking_ids = line.order_id.picking_ids
                    for picking in picking_ids:
                        move_ids = picking.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
                        move_line_ids = picking.move_line_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
                       
                        if move_line_ids:
                            for move_line in move_line_ids:
                                query = "DELETE FROM stock_move_line WHERE id = %s" %(move_line.id)
                                self.env.cr.execute(query)
                        if move_ids:
                            for move in move_ids:
                                query = "DELETE FROM stock_move WHERE id = %s" %(move.id)
                                self.env.cr.execute(query)
                        query = """
                                INSERT INTO stock_move(PRODUCT_ID,PRODUCT_UOM_QTY,PICKING_ID,NAME,PRODUCT_UOM,DATE,COMPANY_ID,LOCATION_ID,LOCATION_DEST_ID,PROCURE_METHOD)
                                VALUES (%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s')
                        """ %(product_id,'0',picking.id,product_name,uom_id,date.today().strftime("%Y-%m-%d"),company_id,picking.location_id.id,picking.location_dest_id.id,'make_to_stock')
                        self._cr.execute(query)
        return True