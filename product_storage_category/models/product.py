# -*- coding: utf-8 -*-
from odoo import models,fields,api

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
                print('\n\n=====putaway_rule_id==',putaway_rule_id)
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


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # def action_apply_inventory(self):
    #     res = super(StockQuant,self).action_apply_inventory()
    #     for quant in self:
    #         product_id = quant.product_id
    #         for storage_line in product_id.product_storage_line_ids:
    #             storage_line.storage_category_id.update_putaway_rule()
    #     return res 

    def action_apply_inventory(self):
        res = super(StockQuant,self).action_apply_inventory()
        for quant in self:
            product_id = quant.product_id
            datas =  product_id.with_context(location_dest_id=self.location_id).get_rule_lines()
        #     for storage_line in product_id.product_storage_line_ids:
        #         storage_line.storage_category_id.update_putaway_rule()
        return res 


    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Create or update move lines.
        """
        res = super(StockQuant,self)._update_reserved_quantity(product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False)
        for quant in self:
            product_id = quant.product_id
            for storage_line in product_id.product_storage_line_ids:
                storage_line.storage_category_id.update_putaway_rule()
        return res

    @api.model
    def _unlink_zero_quants(self):
        print('\n\n\n====_unlink_zero_quants=====================')
        """ _update_available_quantity may leave quants with no
        quantity and no reserved_quantity. It used to directly unlink
        these zero quants but this proved to hurt the performance as
        this method is often called in batch and each unlink invalidate
        the cache. We defer the calls to unlink in this method.
        """
        precision_digits = max(6, self.sudo().env.ref('product.decimal_product_uom').digits * 2)
        # Use a select instead of ORM search for UoM robustness.
        query = """SELECT id FROM stock_quant WHERE (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
                                                     AND round(reserved_quantity::numeric, %s) = 0
                                                     AND (round(inventory_quantity::numeric, %s) = 0 OR inventory_quantity IS NULL)
                                                     AND user_id IS NULL;"""
        params = (precision_digits, precision_digits, precision_digits)
        self.env.cr.execute(query, params)
        quants = []
        for quant in self.env.cr.dictfetchall():
            quants.append(quant['id'])
        quant_ids = self.env['stock.quant'].search([('id','in',quants)])

        for quant in quant_ids:
            product_id = quant.product_id
            location_id = quant.location_id
            storage_category_id  = location_id.storage_category_id
            if storage_category_id  and product_id.product_storage_line_ids:
                storage_line_ids = product_id.product_storage_line_ids.filtered(lambda x:x.storage_category_id and x.storage_category_id.id ==  storage_category_id.id)
            if storage_category_id:
                query1 = """SELECT id from stock_putaway_rule WHERE LOCATION_IN_ID='%s' and  PRODUCT_ID='%s' and STORAGE_CATEGORY_ID='%s'""" %(location_id.id,product_id.id,storage_category_id.id)
                self._cr.execute(query1)
                rules = []
                for row in self._cr.fetchall():
                    rules.append(row[0])  
                rule_ids = self.env['stock.putaway.rule'].sudo().search([('id','in',rules)])
                for rule in rule_ids:
                    rule.unlink()
        quant_ids.sudo().unlink()

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_rule_lines(self):
        lines = []
        # destination_id = self.location_dest_id
        destination_id = False
        if 'location_dest_id' in self._context and self._context['location_dest_id']:
            destination_id = self._context['location_dest_id']
        if destination_id:
            storage_category_lines = self.product_storage_line_ids
            for line in storage_category_lines:
                storage_category_id = line.storage_category_id
                domain = [
                    # ('storage_category_id','=',storage_category_id.id),
                    ('location_id','=',destination_id.id),
                    ('id','!=',destination_id.id),
                ]
                location_ids = self.env['stock.location'].search(domain)
                rule_ids = self.env['stock.putaway.rule'].search([('storage_category_id','=',storage_category_id.id)])
                location_rule_ids = []
                left_location_ids = []
                for rule in rule_ids:
                    location_rule_ids += rule.location_out_id.ids  
                for location in location_ids:
                    if location.id not in location_rule_ids:
                        left_location_ids.append(location.id)
                vals = {
                    'product_id':self.id,
                    'location_in_id':destination_id.id,
                    'storage_category_id':storage_category_id.id,
                }
                if left_location_ids:
                    vals.update({'location_out_id':left_location_ids[0]})
                    rule_id = self.env['stock.putaway.rule'].create(vals)
        return True

        # for product_line in storage.product_capacity_ids:
        #             product_id = product_line.product_id
        #             if product_id and not product_id.qty_available:
        #                 rules = []
        #                 query1 = """SELECT id from stock_putaway_rule WHERE PRODUCT_ID='%s'""" %(product_id.id)
        #                 self._cr.execute(query1)
        #                 for row in self._cr.fetchall():
        #                     rules.append(row[0])                        
        #                 rule_ids = self.env['stock.putaway.rule'].sudo().search([('id','in',rules)])
        #                 storage_location_rule_ids = rule_ids.filtered(lambda x:x.location_out_id.storage_category_id and x.location_out_id.storage_category_id.id == storage.id)
        #                 if storage_location_rule_ids:
        #                     for rule in storage_location_rule_ids:
        #                         rule.unlink()

    # def write(self,vals):
    #     res = super(StockQuant,self).write(vals)
    #     print('\n\n\n=111111111111====vals=========',vals)
    #     if 'quantity' in vals and  vals['quantity']:
    #         for quant in self:
    #             product_id = quant.product_id
    #             for storage_line in product_id.product_storage_line_ids:
    #                 storage_line.storage_category_id.update_putaway_rule()
    #     return res

