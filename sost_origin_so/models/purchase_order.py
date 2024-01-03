# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.depends('order_line.move_dest_ids',
            'order_line.move_dest_ids.group_id',
            'order_line.move_dest_ids.group_id.sale_id',
            'origin',
            'order_line.po_origin','order_line.sost_so_id')
    def _compute_sost_so(self):
        for order in self:
            orders = []
            order_id = [(6,0,[])]
            order_id = order.order_line.move_dest_ids.group_id.sale_id | order.order_line.move_ids.move_dest_ids.group_id.sale_id
            if order_id:
                orders += order_id.ids
            for line in order.order_line.filtered(lambda x:x.sost_so_id):
                orders.append(line.sost_so_id.id)

            if order.origin:
                origins = order.origin.split('S')
                origin_data = []
                for origin in origins:
                    if origin:
                        order_name = 'S'
                        for letter in origin:
                            if letter.isalnum() and len(order_name) < 6:
                                order_name += letter
                            else:
                                break
                        if order_name:
                            origin_data.append(order_name)
                for ord_name in origin_data:
                    so_order_id = self.env['sale.order'].search([('name','=',ord_name)])
                    if so_order_id:
                        orders.append(so_order_id.id)
            order.order_ids = [(6,0,list(set(orders)))]

    order_ids = fields.Many2many('sale.order',string="Sale Origin",compute="_compute_sost_so",store=True)

    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def get_order(self,po_origin):
        origins = po_origin
        origins = origins.split('S')
        origin_data = []
        orders = []
        origin_data = []
        for origin in origins:
            if origin:
                order_name = 'S'
                for letter in origin:
                    if letter.isalnum() and len(order_name) < 6:
                        order_name += letter
                    else:
                        break
                if order_name:
                    origin_data.append(order_name)
        for ord_name in origin_data:
            order = self.env['sale.order'].search([('name','=',ord_name)])
            if order:
                orders.append(order)
        return orders

    @api.depends('move_dest_ids',
            'move_dest_ids.group_id',
            'move_dest_ids.group_id.sale_id',
            'product_id','order_id.order_ids','po_origin','orderpoint_id')
    def _compute_sost_so(self):
        for line in self:
            sost_so_id = False
            order_ids = line.move_dest_ids.group_id.sale_id | line.move_ids.move_dest_ids.group_id.sale_id
            if order_ids:
                sost_so_id = order_ids[0]
            if not sost_so_id and line.po_origin:
                order_ids = line.get_order(line.po_origin)
                if order_ids:
                    sost_so_id = order_ids[0]
            if sost_so_id:
                sost_so_id = sost_so_id.id
            line.sost_so_id = sost_so_id
            line.sost_order = ','.join(order.name for order in list(set(order_ids))) if order_ids else 'Stock'

    sost_so_id = fields.Many2one('sale.order',string="Sale Order",compute="_compute_sost_so",store=True)
    sost_order = fields.Char(string="Order",compute="_compute_sost_so")
    po_origin = fields.Char(string="SO Origin")

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super()._prepare_purchase_order_line_from_procurement(product_id, product_qty, product_uom, company_id, values, po)
        if po.origin:
            res['po_origin'] = po.origin
            orders = []
            origins = po.origin
            origins = origins.split('S')
            origin_data = []
            orders = []
            origin_data = []
            for origin in origins:
                if origin:
                    order_name = 'S'
                    for letter in origin:
                        if letter.isalnum() and len(order_name) < 6:
                            order_name += letter
                        else:
                            break
                    if order_name:
                        origin_data.append(order_name)
            for ord_name in origin_data:
                order = self.env['sale.order'].search([('name','=',ord_name)])
                if order:
                    orders.append(order)
            if orders:
                print('\n\n\n=====orders===',orders,list(set(orders)))
                res['sost_order'] = ','.join(order.name for order in list(set(orders))) if orders else 'Stock'
                orders = orders[0]
                res['sost_so_id'] = orders.id
        return res

