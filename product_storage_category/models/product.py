# -*- coding: utf-8 -*-

from odoo import models,fields,api

class ProductStorageCategoryLines(models.Model):
    _name = 'product.storage.category.lines'
    _description = 'Product Storage Category Lines'


    storage_category_id = fields.Many2one('stock.storage.category',string="Storage Capacity ")
    storage_capacity = fields.Float(string="Storage Capacity")
    product_id = fields.Many2one('product.product',string="Product")
    product_tmp_id = fields.Many2one('product.template',string="Product")
    putaway_rule_id = fields.Many2one('stock.putaway.rule',string="Putaway Rule",ondelete="cascade")
    active = fields.Boolean(string="Active",default=True)

    def unlink(self):
        for record in self:
            # rule_id = self.env['stock.putaway.rule'].search([('prod_storage_category_line_id','=',record.id)])
            if 'unlink_rule' in self._context:
                return super(ProductStorageCategoryLines, self).unlink()
            if record.putaway_rule_id:
                record.putaway_rule_id.with_context(unlink_rule=1).unlink()
        super(ProductStorageCategoryLines, self).unlink()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_storage_line_ids = fields.One2many('product.storage.category.lines','product_tmp_id',string="Lines")

    def update_storage_capacity(self):
        for storage_line in self.product_storage_line_ids:
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

                putaway_rule_id = storage_line.storage_category_id.update_putaway_rule()
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
