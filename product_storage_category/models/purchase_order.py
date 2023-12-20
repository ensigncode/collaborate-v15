# -*- coding: utf-8 -*-
from odoo import models,fields,api , _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    create_product_rule = fields.Boolean(string="Create Product Rule",copy=False)
    done_product_rule = fields.Boolean(string="Done Product Rule",copy=False)
    issue_product_rule = fields.Boolean(string="Issue Product Rule",copy=False)

class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_main_location(self):
        main_destination_id = self
        if main_destination_id:
            count = 0
            while count == 0:
                if main_destination_id.location_id and main_destination_id.location_id.usage == 'internal':
                    main_destination_id = main_destination_id.location_id
                else:
                    count = 1
        return main_destination_id


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

    def get_location_in(self,out_location,storage_category_id):
        get_location_in = False
        print('\n\n====out_location====',out_location)



        get_all_location = {}
        storage_category_id = self.env['stock.storage.category'].browse(storage_category_id)
        main_destination_id = self.env['stock.location'].browse(out_location)
        if main_destination_id:
            get_all_location.update({main_destination_id.display_name.count('/'):main_destination_id})
            count = 0
            while count == 0:
                if main_destination_id.location_id and main_destination_id.location_id.usage == 'internal':
                    main_destination_id = main_destination_id.location_id
                    get_all_location.update({main_destination_id.display_name.count('/'):main_destination_id})
                else:
                    get_all_location.update({main_destination_id.display_name.count('/'):main_destination_id})
                    count = 1
        count = 0
        while count == 0:
            location_id = self.env['stock.location'].search([('location_id','=',main_destination_id.id)])
            if location_id:
                get_all_location.update({location_id[0].display_name.count('/'):location_id})
                main_destination_id = location_id[0]
            else:
                count = 1

        print('\n\n=======get_all_location=========',get_all_location)
        if storage_category_id and storage_category_id.storage_location and get_all_location:
            find_stock_category = storage_category_id.storage_location - 1
            
            if find_stock_category in list(get_all_location.keys()):
                get_location_in = get_all_location[find_stock_category]
                get_location_in = get_location_in[-1]

                print('\n\n===222222222====get_location_in======',get_location_in)

        return get_location_in


    def update_po_product_putaway_rule_data(self):
        line_data = []
        occupied_locations = []
        no_empty_location_found = False
        location_dest_id = self.picking_type_id.default_location_dest_id
        main_destination_id = location_dest_id.get_main_location()

        for line in self.order_line:
            product_id = line.product_id
            datas =  product_id.get_rule_lines(location_dest_id,occupied_locations)

            print('\n\n===datas==',datas)
            
            if datas['create_product_rule']:
                line.create_product_rule = True
                if not datas['issue_product_rule']:
                    data_vals = datas['vals']
                    data_vals.update({'product_id':product_id.id,'location_in_id':location_dest_id.id,'fix_location':True})
                    line.issue_product_rule = False
                    line_data.append(data_vals)
                    occupied_locations.append(datas['occupied_location_id'])
                else:
                    no_empty_location_found = True
                    line.issue_product_rule = True
                    data_vals = datas['vals']
                    data_vals.update({'product_id':product_id.id})
                    line_data.append(data_vals)

                    
        rule_po_line_ids =  self.order_line.filtered(lambda x:x.create_product_rule and not x.issue_product_rule)
        if no_empty_location_found and line_data:
            rule_line_data = []
            for l_data in line_data:
                l_data.update({'operation_type':'existing','location_in_id':location_dest_id.id})
                rule_line_data.append((0,0,l_data))
            rule_vals = {'po_id':self.id,'product_putaway_rule_line_ids':rule_line_data}
            rule_id = self.env['product.putaway.rule'].create(rule_vals)
            # print('\n==11111111======rule_id======',rule_id)
            return {
                'name': _('Putaway Rule'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'product.putaway.rule',
                'target': 'new',
                'res_id': rule_id.id,
            }
        elif line_data:
            for l_data in line_data:
                l_data.pop('fix_location')
                location_in_id = self.get_location_in(l_data['location_out_id'],l_data['storage_category_id'])
                # print('\n==2222222222======location_in_id======',location_in_id)
                if location_in_id:
                    l_data.update({'location_in_id':location_in_id.id})
                else:
                    l_data.update({'location_in_id':main_destination_id.id})
                if 'storage_category_id' in l_data:
                    l_data.pop('storage_category_id')
                rule_id = self.env['stock.putaway.rule'].create(l_data)
                # print('\n==2222222222======rule_id======',rule_id)
        self.with_context(update_po=1).button_confirm()
        return True   

    def button_confirm(self):
        if 'update_po' not in self._context:
            self.update_po_product_putaway_rule_data()
        res = super(PurchaseOrder,self).button_confirm()
        return res

