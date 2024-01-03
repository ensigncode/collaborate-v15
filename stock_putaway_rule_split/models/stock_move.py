from odoo import api, fields, models, _

from itertools import groupby
from odoo.tools.float_utils import float_compare

class StockMove(models.Model):
    _inherit = "stock.move"

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        grouped_moves = groupby(sorted(self, key=lambda m: [f.id for f in m._key_assign_picking()]), key=lambda m: [m._key_assign_picking()])
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*list(moves))
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()
            if picking:
                # If a picking is found, we'll append `move` to its move list and thus its
                # `partner_id` and `ref` field will refer to multiple records. In this
                # case, we chose to wipe them.
                vals = {}
                if any(picking.partner_id.id != m.partner_id.id for m in moves):
                    vals['partner_id'] = False
                if any(picking.origin != m.origin for m in moves):
                    vals['origin'] = False
                if vals:
                    picking.write(vals)
            else:
                # Don't create picking for negative moves since they will be
                # reverse and assign to another picking
                moves = moves.filtered(lambda m: float_compare(m.product_uom_qty, 0.0, precision_rounding=m.product_uom.rounding) >= 0)
                if not moves:
                    continue
                new_picking = True
                picking = Picking.create(moves._get_new_picking_values())

            po_id = self.env['purchase.order'].sudo().search([('name', '=', picking.origin)], limit=1)
            po_line_ids = po_id.order_line
            for move in moves:
                po_move_line_id = po_line_ids.filtered(lambda pml: pml.product_id.id == move.product_id.id)
                if po_move_line_id:
                    qty_list = po_move_line_id[0].with_context(dest_loc_id=move.location_dest_id)._prepare_split_stock_putaway(po_move_line_id[0].product_qty)
                    for move_id, qty in {index==0 and move or move.copy({'picking_id':picking.id}): qt for index, qt in enumerate(qty_list)}.items():
                        move_id.write({'product_uom_qty':qty})
                
            moves.write({'picking_id': picking.id})
            moves._assign_picking_post_process(new=new_picking)
        return True