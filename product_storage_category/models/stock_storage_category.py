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
		location_out_id = self.env['stock.location'].search([('id', 'child_of', input_loc.id), '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id),('storage_category_id','=',self.id)], limit=1)
		if not location_out_id:
			location_out_id = self.env['stock.location'].search([('id', 'child_of', input_loc.id), '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)], limit=1)
		return {'location_out_id':location_out_id,'location_in_id':input_loc or False}

	def update_putaway_rule(self):
		putaway_rule_id = False
		for storage in self:
			if storage.auto_putaway_rule:
				location_vals = self._default_location_id()
				location_out_id = location_vals['location_out_id']
				location_in_id = False
				if 'location_in_id' in location_vals.keys() and  location_vals['location_in_id']:
					location_in_id =  location_vals['location_in_id']
					location_in_id = location_in_id.id
				else:
					location_in_id = location_out_id.id

				storage_category_id = self
				if location_out_id:
					for product_line in storage.product_capacity_ids:
						product_id = product_line.product_id
						if product_id and not product_id.qty_available:
							rules = []
							query1 = """SELECT id from stock_putaway_rule WHERE PRODUCT_ID='%s'""" %(product_id.id)
							self._cr.execute(query1)
							for row in self._cr.fetchall():
								rules.append(row[0])						
							rule_ids = self.env['stock.putaway.rule'].sudo().search([('id','in',rules)])
							storage_location_rule_ids = rule_ids.filtered(lambda x:x.location_out_id.storage_category_id and x.location_out_id.storage_category_id.id == storage.id)
							if storage_location_rule_ids:
								for rule in storage_location_rule_ids:
									rule.unlink()
						else:
							domain = [
								('storage_category_id','=',self.id),
								('product_id','=',product_line.product_id.id),
								('location_out_id','=',location_out_id.id),
							]
							rule_id = self.env['stock.putaway.rule'].search(domain)
							if not rule_id:
								vals = {
									'storage_category_id':self.id,
									'product_id':product_line.product_id.id,
									'location_out_id':location_out_id.id,
									'location_in_id':location_in_id,
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
