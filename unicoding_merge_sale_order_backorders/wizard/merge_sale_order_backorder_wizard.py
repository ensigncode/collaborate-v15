# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class MergeSaleOrderBackorder(models.TransientModel):
    _name = 'merge.sale.order.backorder'
    _description = 'Merge Sale Order Backorder'

    order_ids = fields.Many2many('sale.order', string='Orders')
    picking_ids = fields.Many2many('stock.picking', string='Backorders')
    

    

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        order_ids = self._context.get('active_ids', [])
        if 'order_ids' in fields:
            res['order_ids'] = [(6, 0, order_ids)]
        if 'picking_ids' in fields:
            res['picking_ids'] = [(6, 0, self.env['stock.picking'].search([('sale_id', 'in', order_ids), ('state', 'not in', ('done', 'cancel'))]).ids)]

        return res


    def merge_pciking_create_order(self):
        self.ensure_one()

        sale_orders = self.order_ids
        partner = sale_orders[0].partner_id.id
        if any(order.partner_id.id != partner for order in sale_orders):
            raise UserError(
                _('Please select Sale orders whose Customers are same to '
                    ' perform the Merge Operation.'))

        so = self.env['sale.order'].with_context({
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [partner]
            }).create({'partner_id': partner})
        default = {'order_id': so.id}
        
        
        default = {'order_id': so.id}
        for order in sale_orders:
            for line in order.order_line:
                existing_so_line = False
                if so.order_line:
                    for soline in so.order_line:
                        if line.product_id == soline.product_id and \
                                line.price_unit == soline.price_unit:
                            existing_so_line = soline
                            break
                if existing_so_line:
                    existing_so_line.product_uom_qty += line.product_uom_qty - line.qty_delivered
                    
                    so_taxes = [tax.id for tax in existing_so_line.tax_id]
                    [so_taxes.append((tax.id)) for tax in line.tax_id]
                    existing_so_line.tax_id = [(6, 0, so_taxes)]
                else:
                    line.copy(default=default | {'product_uom_qty': line.product_uom_qty - line.qty_delivered})
                
                # update so line  qty = delivered
                line.product_uom_qty = line.qty_delivered

        for picking_id in self.picking_ids:
            picking_id.unlink()
        
        so.message_post(body=_('Created from Sale Orders %s') % (', '.join(sale_orders.mapped('name'))))

        
        view = self.env.ref('sale.view_order_form')
        return {
            'name': _('View Sale'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'fullscreen',
            'res_id': so.id,
            'context': self.env.context,
        }