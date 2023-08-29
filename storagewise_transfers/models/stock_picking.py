# -*- coding: utf-8 -*-
from odoo import models,fields,api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(StockMove,self)._prepare_move_line_vals()
        if 'default_location_dest_id' in self.env.context and self.env.context['default_location_dest_id']:
            default_location_dest_id = self.env.context['default_location_dest_id']
            res.update({'location_dest_id':default_location_dest_id.id})
        return res

    def apply_product_rule(self):
        done_moves = []
        move = self
        for move in self:
            move.move_line_ids.unlink()
            domain = [('product_id','=',move.product_id.id)]
            rule_ids = self.env['stock.putaway.rule'].search(domain)
            location_out_ids = []
            rule_vals = {}
            for rule in rule_ids:
                rule_line_ids = rule.storage_category_id.product_capacity_ids.filtered(lambda x:x.product_id.id == move.product_id.id)
                if rule_line_ids:
                    rule_vals.update({rule.location_out_id:rule_line_ids[0].quantity})
            storage_category_ids = self.env['stock.storage.category.capacity'].search([('product_id','=',move.product_id.id)])
            qty_lines = {}
            if storage_category_ids and move.id not in done_moves:
                move_qty = move.product_uom_qty
                move_line_vals_list = []
                for rv in rule_vals:
                    quantity = rule_vals[rv]
                    move_line_vals = {}
                    if quantity > move_qty and move_qty > 0:
                        move_line_vals = move.with_context({'default_location_dest_id':rv})._prepare_move_line_vals(quantity=move_qty)
                        move_line_vals.update({'qty_done':move_qty})
                        move_qty -= move_qty
                    elif quantity < move_qty and move_qty > 0:
                        move_line_vals = move.with_context({'default_location_dest_id':rv})._prepare_move_line_vals(quantity=quantity)
                        move_line_vals.update({'qty_done':quantity})
                        move_qty = move_qty - quantity 
                    if move_line_vals:
                        move_line_vals_list.append(move_line_vals)
                if move_qty > 0:
                    extra_move_line_vals = move._prepare_move_line_vals(quantity=move_qty)
                    extra_move_line_vals.update({'qty_done':move_qty})
                    extra_move_line_vals.update({'qty_done':move_qty})
                    move_line_vals_list.append(extra_move_line_vals)
                if move_line_vals_list:
                    self.env['stock.move.line'].create(move_line_vals_list)
        return True    

    def _action_assign(self):
        res = super(StockMove, self)._action_assign()
        move_id = self
        if self and self[0].picking_id.picking_type_id.code == 'incoming':
            self.apply_product_rule()       
        return res


    # def apply_product_rule(self):
    #     done_moves = []
    #     move = self
    #     for move in self:
    #         domain = [('product_id','=',move.product_id.id),('company_id','=',self.env.company_id)]
    #         rule_ids = self.env['stock.putaway.rule'].search(domain)

    #         sub_location_ids = []
    #         for rule in rule_ids:
    #             sub_location_ids.append(rule.location_out_id)
            
    #         qty_lines = {}
    #         if rule_ids and move.id not in done_moves:
    #             # sub_location_id = rule_ids.location_out_id

    #             storage_capacity_line_id = rule_ids.storage_category_id.product_capacity_ids.filtered(lambda x:x.product_id.id == move.product_id.id)
    #             quantity = storage_capacity_line_id.quantity

    #             qty = move.product_uom_qty
    #             extra_qty = 0
    #             if move.product_uom_qty > quantity:
    #                 qty = quantity
    #                 extra_qty = move.product_uom_qty - quantity

    #             qty_lines.update({'qty':qty,'extra_qty':extra_qty})
    #             move.move_line_nosuggest_ids.unlink()

    #             if qty_lines:
    #                 move_line_vals_list = []

    #                 if sub_location_id:
    #                     move_line_vals = move.with_context({'default_location_dest_id':sub_location_id})._prepare_move_line_vals(quantity=qty_lines['qty'])
    #                 else:
    #                     move_line_vals = move._prepare_move_line_vals(quantity=qty_lines['qty'])
                    
    #                 if move_line_vals:
    #                     move_line_vals.update({'qty_done':qty_lines['qty']})
    #                     move_line_vals_list.append(move_line_vals)

    #                 if qty_lines['extra_qty'] > 0:
    #                     extra_move_line_vals = move._prepare_move_line_vals(quantity=qty_lines['extra_qty'])
    #                     extra_move_line_vals.update({'qty_done':qty_lines['extra_qty']})
    #                     move_line_vals_list.append(extra_move_line_vals)

    #                 if move_line_vals_list:
    #                     self.env['stock.move.line'].create(move_line_vals_list)
    #     return True