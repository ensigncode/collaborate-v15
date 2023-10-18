# -*- coding: utf-8 -*-
from odoo import models,fields,api

class StockStorageCategoryCapacity(models.Model):
    _inherit = 'stock.storage.category.capacity'

    product_tmp_id = fields.Many2one('product.template',string="Template")
    prod_storage_category_line_id = fields.Many2one('product.storage.category.lines',string="Category Lines",ondelete="cascade")
    active = fields.Boolean(string="Active",default=True)

    def unlink(self):
        for record in self:
        	if record.prod_storage_category_line_id:
        		record.prod_storage_category_line_id.unlink()
        super(StockStorageCategoryCapacity, self).unlink()

    @api.model
    def create(self,vals):
    	res = super(StockStorageCategoryCapacity,self).create(vals)
    	if not res.prod_storage_category_line_id:
    		prod_storage_category_line_id = self.env['product.storage.category.lines'].create({'storage_category_id':res.storage_category_id.id,'storage_capacity':res.quantity,'product_tmp_id':res.product_id.product_tmpl_id.id})
    		res.prod_storage_category_line_id = prod_storage_category_line_id.id
    	return res

    
class StockStorageCategory(models.Model):
    _inherit = 'stock.storage.category'

    auto_putaway_rule = fields.Boolean(string="Auto Putaway Rules")

    def _default_location_id(self):
        wh = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        input_loc, _ = wh._get_input_output_locations(wh.reception_steps, wh.delivery_steps)
        return input_loc

    def update_putaway_rule(self):
    	putaway_rule_id = False
    	for storage in self:
    		if storage.auto_putaway_rule:
    			default_location_id = self._default_location_id()
    			storage_category_id = self
    			if default_location_id:
	    			for product_line in storage.product_capacity_ids:
	    				domain = [
	    					('storage_category_id','=',self.id),
	    					('product_id','=',product_line.product_id.id),
	    					('location_out_id','=',default_location_id.id),
						]
	    				rule_id = self.env['stock.putaway.rule'].search(domain)
	    				if not rule_id:
	    					vals = {
	    						'storage_category_id':self.id,
	    						'product_id':product_line.product_id.id,
	    						'location_out_id':default_location_id.id,
	    						'location_in_id':default_location_id.id,
	    					}
	    					putaway_rule_id = self.env['stock.putaway.rule'].create(vals)
    	return putaway_rule_id
    			
    @api.model
    def create(self,vals):
    	res = super(StockStorageCategory,self).create(vals)
    	for storage in res:
    		storage.update_putaway_rule()
    	return res

    def write(self,vals):
    	res = super(StockStorageCategory,self).write(vals)
    	for storage in self:
    		storage.update_putaway_rule()
    	return res


class StockPutawayRule(models.Model):
    _inherit = 'stock.putaway.rule'

    prod_storage_category_line_id = fields.Many2one('product.storage.category.lines',string="Category Lines",ondelete="cascade")
    