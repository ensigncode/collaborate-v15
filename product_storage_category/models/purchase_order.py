# -*- coding: utf-8 -*-
from odoo import models,fields,api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    create_product_rule = fields.Boolean(string="Create Product Rule")
    done_product_rule = fields.Boolean(string="Done Product Rule")
    issue_product_rule = fields.Boolean(string="Issue Product Rule")



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def create_product_putaway_rule(self,create_rule,no_vals_found):
        line_data = []
        used_location = []
        for rule in create_rule:
            line_data.append((0,0,rule))
        for rule in no_vals_found:
            line_data.append((0,0,rule))
        rule_vals = {'product_putaway_rule_line_ids':line_data}
        rule_id = self.env['product.putaway.rule'].create(rule_vals)
        return {
            'name': 'Putaway Rule',
            'view_mode': 'form',
            'target': 'new',
            'res_id': rule_id.id,
            'res_model': 'product.putaway.rule',
            'type': 'ir.actions.act_window',
        }


    def update_po_product_putaway_rule_data(self):
        line_data = []
        used_location = []

        create_rule = []
        no_vals_found  = []

        location_dest_id = self.picking_type_id.default_location_dest_id

        for line in self.order_line:
            product_id = line.product_id
            datas =  product_id.get_rule_lines()
            print('\n===datas===============',datas)
            if not datas:
                vals = {
                    'product_id':line.product_id.id,
                    'location_in_id':location_dest_id.id,
                }
                no_vals_found.append(vals)
            # else:
            #     no_vals_found.append(datas)
        return no_vals_found

        
        # if no_vals_found:
        #     self.create_product_putaway_rule(create_rule,no_vals_found)
        # else:
        #     if create_rule:
        #         print('\n\n==create_rule==',create_rule)

        #         for rule in create_rule:
        #             print('\n\n==rule_id==',rule)

        #             rule_id = self.env['stock.putaway.rule'].create(rule)
        #             print('\n\n==rule_id==',rule_id)
        # return True

    def update_putaway_rule(self):
        if self.picking_type_id and self.picking_type_id.default_location_dest_id:
            no_vals_found = self.with_context(location_dest_id=self.picking_type_id.default_location_dest_id).update_po_product_putaway_rule_data()
            line_data = []
            used_location = []
            # for rule in create_rule:
            #     line_data.append((0,0,rule))
            for rule in no_vals_found:
                line_data.append((0,0,rule))
            rule_vals = {'product_putaway_rule_line_ids':line_data}
            rule_id = self.env['product.putaway.rule'].create(rule_vals)
            return {
                'name': 'Putaway Rule',
                'view_mode': 'form',
                'target': 'new',
                'res_id': rule_id.id,
                'res_model': 'product.putaway.rule',
                'type': 'ir.actions.act_window',
            }
        return True


    def button_confirm(self):
        # if self.picking_type_id and self.picking_type_id.default_location_dest_id:
        #     self.with_context(location_dest_id=self.picking_type_id.default_location_dest_id).update_po_product_putaway_rule_data()
        res = super(PurchaseOrder,self).button_confirm()
        return res

