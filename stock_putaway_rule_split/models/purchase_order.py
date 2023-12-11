
from lxml import etree

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _create_picking(self):
        """
            Override to stop merging moves when having putaway rules applied
        """
        StockPicking = self.env['stock.picking']
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                # Added merge=False to stop merging because having split moves by putaway rules
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm(merge=False)
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_split_stock_putaway(self, qty):
        """
            Preparing splitting of the stock rules
        """
        dest_location_id = (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location()
        putaway_rules = self.product_id.putaway_rule_ids.filtered(
            lambda p_rule: p_rule.storage_category_id and p_rule.location_in_id.id == dest_location_id
        )
        quantity_list = []
        qty_to_remaining = qty
        for location_id in list(set(putaway_rules.mapped('storage_category_id.location_ids'))):
            product_capacity_lines = location_id.storage_category_id.product_capacity_ids.filtered(
                lambda pc_line: pc_line.product_id.id == self.product_id.id)
            for p_cap_line in product_capacity_lines:
                if qty_to_remaining <= 0:
                    break
                quantity_list.append(
                    p_cap_line.quantity if p_cap_line.quantity <= qty_to_remaining else qty_to_remaining
                )
                qty_to_remaining -= p_cap_line.quantity
        if qty_to_remaining:
            quantity_list.append(qty_to_remaining)
        return quantity_list

    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        price_unit = self._get_stock_move_price_unit()
        qty = self._get_qty_procurement()
        move_dests = self.move_dest_ids or self.move_ids.move_dest_ids
        move_dests = move_dests.filtered(lambda m: m.state != 'cancel' and not m._is_purchase_return())

        if not move_dests:
            qty_to_attach = 0
            qty_to_push = self.product_qty - qty
        else:
            move_dests_initial_demand = self.product_id.uom_id._compute_quantity(
                sum(move_dests.filtered(lambda m: m.state != 'cancel' and not m.location_dest_id.usage == 'supplier').mapped('product_qty')),
                self.product_uom, rounding_method='HALF-UP')
            qty_to_attach = move_dests_initial_demand - qty
            qty_to_push = self.product_qty - move_dests_initial_demand

        qty_to_move = self._prepare_split_stock_putaway(qty_to_push)
        if float_compare(qty_to_attach, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(qty_to_attach, self.product_id.uom_id)
            res.append(self._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom))
        if not float_is_zero(qty_to_push, precision_rounding=self.product_uom.rounding):
            # Added loop to create all moves which has been split
            for qty_to_add in qty_to_move:
                extra_move_vals = self._prepare_stock_move_vals(picking, price_unit, qty_to_add, self.product_id.uom_id)
                extra_move_vals['move_dest_ids'] = False  # don't attach
                res.append(extra_move_vals)
        return res
