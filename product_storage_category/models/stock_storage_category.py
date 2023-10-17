# -*- coding: utf-8 -*-
from odoo import models,fields,api

class StockStorageCategory(models.Model):
    _inherit = 'stock.storage.category'

    auto_putaway_rule = fields.Boolean(string="Auto Putaway Rules")

    def _default_location_id(self):
        wh = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        input_loc, _ = wh._get_input_output_locations(wh.reception_steps, wh.delivery_steps)
        return input_loc

    def update_putaway_rule(self):
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
	    					self.env['stock.putaway.rule'].create(vals)
    	return True
    			
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
