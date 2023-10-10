# -*- coding: utf-8 -*-

from odoo import models,fields,api

class ProductStorageCategoryLines(models.Model):
    _name = 'product.storage.category.lines'
    _description = 'Product Storage Category Lines'


    storage_category_id = fields.Many2one('stock.storage.category',string="Storage Capacity ")
    storage_capacity = fields.Float(string="Storage Capacity")
    product_id = fields.Many2one('product.product',string="Product")

class Product(models.Model):
    _inherit = 'product.product'

    product_storage_line_ids = fields.One2many('product.storage.category.lines','product_id',string="Lines")

    def update_storage_capacity(self):
        for storage_line in self.product_storage_line_ids:
            storage_category_line_ids = False
            if storage_line and storage_line.product_capacity_ids:
                storage_category_line_ids  = storage_line.product_capacity_ids.filtered(lambda x:x.product_id.id == self.id)
                for line in storage_category_line_ids:
                    line.quantity = storage_line.storage_capacity
            if not storage_category_line_ids:
                vals = {
                    'product_id':self.id,
                    'quantity':storage_line.storage_capacity,
                    'storage_category_id':storage_line.storage_category_id.id,
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
        for product in self:
            product.update_storage_capacity()
        return res
