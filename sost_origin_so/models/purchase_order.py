# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.move_dest_ids','order_line.move_dest_ids.group_id','order_line.move_dest_ids.group_id.sale_id')
    def _compute_sost_so(self):
        for order in self:
            order_id = [(6,0,[])]
            order_ids = order.order_line.move_dest_ids.group_id.sale_id | order.order_line.move_ids.move_dest_ids.group_id.sale_id
            if order_ids:
                order_id = [(6,0,order_ids.ids)]
            order.order_ids = order_id

    order_ids = fields.Many2many('sale.order',string="Sale Origin",compute="_compute_sost_so",store=True)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('move_dest_ids',
            'move_dest_ids.group_id',
            'move_dest_ids.group_id.sale_id',
            'product_id','order_id.order_ids')
    def _compute_sost_so(self):
        for line in self:
            sost_so_id = False
            order_ids = line.move_dest_ids.group_id.sale_id | line.move_ids.move_dest_ids.group_id.sale_id
            if order_ids:
                sost_so_id = order_ids[0]
            line.sost_so_id = sost_so_id
            line.sost_order = ','.join(order.name for order in order_ids) if order_ids else 'Stock'

    sost_so_id = fields.Many2one('sale.order',string="Sale Order",compute="_compute_sost_so",store=True)
    sost_order = fields.Char(string="Order",compute="_compute_sost_so")
