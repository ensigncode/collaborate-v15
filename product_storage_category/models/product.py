# -*- coding: utf-8 -*-
from odoo import models,fields,api, _

class ProductStorageCategoryLines(models.Model):
    _name = 'product.storage.category.lines'
    _description = 'Product Storage Category Lines'

    storage_category_id = fields.Many2one('stock.storage.category',string="Storage Capacity ")
    storage_capacity = fields.Float(string="Storage Capacity")
    product_id = fields.Many2one('product.product',string="Product")
    product_tmp_id = fields.Many2one('product.template',string="Product")
    putaway_rule_id = fields.Many2one('stock.putaway.rule',string="Putaway Rule")
    # putaway_rule_id = fields.Many2one('stock.putaway.rule',string="Putaway Rule",ondelete="cascade")
    active = fields.Boolean(string="Active",default=True)

    # def unlink(self):
    #     for record in self:
    #         if 'unlink_rule' in self._context:
    #             return super(ProductStorageCategoryLines, self).unlink()
    #         if record.putaway_rule_id:
    #             record.putaway_rule_id.with_context(unlink_rule=1).unlink()
    #     super(ProductStorageCategoryLines, self).unlink()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_storage_line_ids = fields.One2many('product.storage.category.lines','product_tmp_id',string="Lines")

    def update_storage_capacity(self):
        for storage_line in self.product_storage_line_ids:
            # storage_line.storage_category_id.update_putaway_rule()
            product_ids = self.product_variant_ids
            for product in product_ids:
                storage_category_line_ids = False
                query1 = """SELECT id from stock_storage_category_capacity WHERE STORAGE_CATEGORY_ID='%s' and PRODUCT_ID='%s'""" %(storage_line.storage_category_id.id,product.id)
                self._cr.execute(query1)
                for row in self._cr.fetchall():
                    storage_category_line_ids = self.env['stock.storage.category.capacity'].sudo().browse(row[0])
                    for line in storage_category_line_ids:
                        line.update({'quantity':storage_line.storage_capacity,'active':True})
                
                if not storage_category_line_ids:
                    vals = {
                        'product_tmp_id':product.product_tmpl_id.id,
                        'product_id':product.id,
                        'quantity':storage_line.storage_capacity,
                        'storage_category_id':storage_line.storage_category_id.id,
                        'company_id':self.env.company.id,
                        'prod_storage_category_line_id':storage_line.id,
                    }
                    storage_category_line_ids = self.env['stock.storage.category.capacity'].create(vals)
                putaway_rule_id = storage_line.storage_category_id.with_context(update_putaway_rule=1).update_putaway_rule()
                if putaway_rule_id:
                    putaway_rule_id.prod_storage_category_line_id = storage_line.id
                    storage_line.putaway_rule_id = putaway_rule_id.id
        return True

    @api.model
    def create(self,vals):
        res = super(ProductTemplate,self).create(vals)
        res.update_storage_capacity()
        return res

    def write(self,vals):
        res = super(ProductTemplate,self).write(vals)
        for product in self:
            product.update_storage_capacity()
        if 'active' in vals and not  vals['active']:
            for product in self:
                domain = ['|',('product_tmp_id','=',product.id),('product_id','in',product.product_variant_ids.ids)]
                category_capacity_ids = self.env['stock.storage.category.capacity'].search(domain)
                for cat_capacity in category_capacity_ids:
                    cat_capacity.active = False
        return res



class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_rule_lines(self,location_dest_id,occupied_locations):
        lines = []
        destination_id = location_dest_id
        vals = {}
        create_product_rule = False
        issue_product_rule = False
        occupied_location_id = False
        if destination_id:
            storage_category_lines = self.product_storage_line_ids
            if not storage_category_lines:
                create_product_rule = False
            
            rule_ids = self.env['stock.putaway.rule'].search([('product_id','=',self.id)])
            # print('\n\n==self.id=rule_ids==',rule_ids,self.id)
            # print('==storage_category_lines=',storage_category_lines)
            if not rule_ids and storage_category_lines:
                if storage_category_lines or not rule_ids:
                    create_product_rule = True
                for line in storage_category_lines:

                    vals = {'product_id':self.id,'location_in_id':destination_id.id}
                    storage_category_id = line.storage_category_id
                    domain = [
                        ('storage_category_id','=',storage_category_id.id),
                    ]
                    storage_category_location_ids = self.env['stock.location'].search(domain)
                    # print('\n=====storage_category_location_ids===',storage_category_location_ids)
                    if not storage_category_location_ids:
                        create_product_rule = False
                    if storage_category_location_ids and create_product_rule:
                        storage_category_location_ids = storage_category_location_ids.filtered(lambda x:x.id not in occupied_locations)
                        rule_ids = self.env['stock.putaway.rule'].search([('location_out_id','in',storage_category_location_ids.ids)])
                        location_rule_ids = []
                        left_location_ids = []
                        if not rule_ids:
                            left_location_ids = storage_category_location_ids.ids
                        else:
                            for rule in rule_ids:
                                location_rule_ids += rule.location_out_id.ids 
                            for location in storage_category_location_ids:
                                if location.id not in location_rule_ids:
                                    left_location_ids.append(location.id)

                        if left_location_ids:
                            issue_product_rule = False
                            vals.update({'location_out_id':left_location_ids[0]})
                            occupied_location_id = left_location_ids[0]

                        else:
                            issue_product_rule = True

        if create_product_rule and not occupied_location_id and  not rule_ids:
            issue_product_rule = True
        return {'create_product_rule':create_product_rule,'issue_product_rule':issue_product_rule,'occupied_location_id':occupied_location_id,'vals':vals} 


