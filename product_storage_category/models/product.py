# -*- coding: utf-8 -*-

from odoo import models,fields,api

class Product(models.Model):
    _inherit = 'product.product'

    storage_category_id = fields.Many2one('stock.storage.category',string="Storage Capacity")
    storage_capacity = fields.Float(string="Storage Capacity")

    def update_storage_capacity(self):
        storage_category_line_ids = False
        if self.storage_category_id and self.storage_category_id.product_capacity_ids:
            storage_category_line_ids  = self.storage_category_id.product_capacity_ids.filtered(lambda x:x.product_id.id == self.id)
            for line in storage_category_line_ids:
                line.quantity = self.storage_capacity
                
        if not storage_category_line_ids:
            vals = {
                'product_id':self.id,
                'quantity':self.storage_capacity,
                'storage_category_id':self.storage_category_id.id,
                'company_id':self.env.company.id,
            }
            self.env['stock.storage.category.capacity'].create(vals)
        return True

    @api.model
    def create(self,vals):
        res = super(Product,self).create(vals)
        res.update_storage_capacity()
        return res

    def write(self,vals):
        res = super(Product,self).write(vals)
        if 'storage_category_id' in vals or 'storage_capacity' in vals:
            for product in self:
                product.update_storage_capacity()
        return res
