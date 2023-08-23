# -*- coding: utf-8 -*-

from odoo import models,fields,api
from datetime import datetime,date

class TransferHandlingUnit(models.TransientModel):
    _name = 'transfer.handling.unit'
    _description = 'Transfer Handling Unit'

    name = fields.Char(default="Handling Unit")
    partner_id = fields.Many2one('res.partner',string="Contact")
    picking_id = fields.Many2one('stock.picking',string="Transfer")
    scheduled_date = fields.Datetime(string="Scheduled Date")
    origin = fields.Char(string="Source Document")
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse")
    need_to_update = fields.Boolean(string="Need To Update")
    product_code = fields.Char(string="Handling Unit")
    transfer_handling_unit_id = fields.Many2one('transfer.handling.unit.line',string="Contact")

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


class TransferHandlingUnitLine(models.TransientModel):
    _name = 'transfer.handling.unit.line'
    _description = 'Transfer Handling Unit Line'

    name = fields.Char(default="Handling Unit")    
    transfer_handling_unit_ids = fields.One2many('transfer.handling.unit','transfer_handling_unit_id',string="Transfer Handling Units")

    def get_product_code(self,picking_id):
        categ_id = self.env['product.category'].search([('is_cos_category','=',True)],limit=1)
        product_code = ''
        move_line = picking_id.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
        if move_line:
            product_code = move_line[-1].product_id.name
        return product_code

    def get_picking_vals(self,picking):
        product_code = self.get_product_code(picking)
        vals = {
                'picking_id':picking.id,
                'partner_id':picking.partner_id.id,
                'scheduled_date':picking.scheduled_date,
                'origin':picking.origin,
                'product_code':product_code,
            }
        return vals

    @api.model
    def default_get(self,vals):
        res = super(TransferHandlingUnitLine,self).default_get(vals)
        picking_ids = self.env['stock.picking'].search([('state','=','assigned'),('is_pick_type','=',True)])
        sequence = 10
        update_product = []
        for picking in picking_ids:
            vals = self.get_picking_vals(picking)
            update_product.append((0,0,vals))
        res['transfer_handling_unit_ids'] = update_product
        return res

    def action_confirm(self):
        categ_id = self.env['product.category'].search([('is_cos_category','=',True)],limit=1)
        done_pickings = []
        if self.transfer_handling_unit_ids:
            for line in self.transfer_handling_unit_ids:

                line.need_to_update = False
                scheduled_date = line.scheduled_date.date()
                sch_date = scheduled_date.strftime('%Y-%m-%d %H:%M:%S')
                origin = line.origin

                # 2023-08-18 09:47:42

                product_id = line.get_product(line.product_code)
                if line.product_code and categ_id and product_id:
                    company_id = self.env.company.id
                    uom_id = product_id.uom_id.id
                    product_name = product_id.display_name
                    product_id = product_id.id
                    move_line = line.picking_id.move_ids_without_package.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
                    done_pickings.append(line.picking_id.id)
                    
                    if move_line:
                        for line in move_line:
                            query = "DELETE FROM stock_move WHERE id = %s" %(line.id)
                            self.env.cr.execute(query)

                    query = """
                            INSERT INTO STOCK_MOVE(PRODUCT_ID,PRODUCT_UOM_QTY,NAME,PICKING_ID,PRODUCT_UOM,DATE,COMPANY_ID,LOCATION_ID,LOCATION_DEST_ID,PROCURE_METHOD)
                            VALUES (%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s')
                    """ %(product_id,'0',product_name,line.picking_id.id,uom_id,sch_date,line.picking_id.company_id.id,line.picking_id.location_id.id,line.picking_id.location_dest_id.id,'make_to_stock')
                    self._cr.execute(query)
                    if origin:
                        order_id = self.env['sale.order'].search([('name','=',origin)])
                        if order_id:
                            order_line = order_id.order_line.filtered(lambda x:x.product_id.categ_id and x.product_id.categ_id.id == categ_id.id and x.product_uom_qty == 0)
                            if order_line:
                                for o_line in order_line:
                                    query = "DELETE FROM sale_order_line WHERE id = %s" %(o_line.id)
                                    self.env.cr.execute(query)
                            query = """
                                    INSERT INTO sale_order_line(PRODUCT_ID,PRODUCT_UOM_QTY,PRICE_UNIT,ORDER_ID,NAME,CUSTOMER_LEAD,PRODUCT_UOM,SEQUENCE)
                                    VALUES (%s,'%s',%s,%s,'%s','%s','%s','%s')
                            """ %(product_id,'0','0',order_id.id,product_name,'0',uom_id,'11')
                            self._cr.execute(query)


                            picking_ids = order_id.picking_ids
                            for picking in picking_ids:
                                if picking.id not in done_pickings:
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
