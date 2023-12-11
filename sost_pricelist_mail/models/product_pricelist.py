# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date,datetime

class PricelistInfo(models.Model):
	_name = 'pricelist.info'
	_description = 'Pricelist Info'

	product_tmpl_id = fields.Many2one('product.template',string="Product")
	pricelist_info_id = fields.Many2one('product.pricelist',string="Product")
	product_variant_id = fields.Many2one('product.product',string="Product Variant")
	currency_id = fields.Many2one('res.currency',string="Currency")
	availablity_message = fields.Char(string="Availablity")
	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	price_unit = fields.Char(string="Price Unit")


class ProductPricelist(models.Model):
	_inherit = 'product.pricelist'


	pricelist_info_ids = fields.One2many('pricelist.info','pricelist_info_id')

	def action_pricelist_info(self):
		pricelist_lines = []
		for item in self.item_ids.filtered(lambda x:x.applied_on in ('1_product','0_product_variant')):
			availablity_message = ''
			vals = item.get_item_data()
			# if item.date_start and item.date_end:
			# 	date_start = item.date_start.date()
			# 	date_end = item.date_end.date()
			# 	availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))

			# if item.date_start and not item.date_end:
			# 	date_start = item.date_start.date()
			# 	date_end = date.today()
			# 	availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))

			# if item.date_end and not item.date_start:
			# 	date_start = date.today()
			# 	date_end = item.date_end.date()
			# 	availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))

			# if not item.date_end and not item.date_start:
			# 	date_start = date.today()
			# 	date_end = date.today()
			# 	availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))
			vals = {
				'product_tmpl_id':item.product_tmpl_id.id if item.product_tmpl_id else False,
				'product_variant_id':item.product_id.id if item.product_id else False,
				'currency_id':item.currency_id.id if item.currency_id else False,
				'availablity_message':vals['availablity_message'],
				'start_date':vals['date_start'],
				'end_date':vals['date_end'],
				'price_unit':item.price,
			}
			pricelist_lines.append((0,0,vals))

		vals = {'pricelist_id':self.id,'update_pricelist_line_ids':pricelist_lines}
		res_id = self.env['update.pricelist'].create(vals)
		return {
			'type': 'ir.actions.act_window',
			'name': _('Pricelist'),
			'res_model': 'update.pricelist',
			'target': 'new',
			'view_mode': 'form',
			'view_id': self.env.ref('sost_pricelist_mail.view_update_pricelist_form').id,
			'res_id':res_id.id,
		}


class ProductPricelistItem(models.Model):
	_inherit = 'product.pricelist.item'

	def get_item_data(self):
		item = self
		date_start = date.today()
		date_end = date.today()
		vals = {'availablity_message':'','start_date':'','end_date':'','date_start':date_start,'date_end':date_end}

		if item.date_start and item.date_end:
			date_start = item.date_start.date()
			date_end = item.date_end.date()
			availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))

		if item.date_start and not item.date_end:
			date_start = item.date_start.date()
			date_end = date.today()
			availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))

		if item.date_end and not item.date_start:
			date_start = date.today()
			date_end = item.date_end.date()
			availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))

		if not item.date_end and not item.date_start:
			date_start = date.today()
			date_end = date.today()
			availablity_message = 'Available from %s - %s' %(date_start.strftime('%d/%m/%Y'),date_end.strftime('%d/%m/%Y'))
		vals.update({'availablity_message':availablity_message,'start_date':date_start.strftime('%d/%m/%Y'),'end_date':date_end.strftime('%d/%m/%Y'),'date_end':date_end,'date_start':date_start})
		return vals




