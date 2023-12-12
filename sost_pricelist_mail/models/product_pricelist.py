# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date,datetime

class ProductPricelist(models.Model):
	_inherit = 'product.pricelist'

	def action_quotation_send(self):
		''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
		self.ensure_one()
		mail_template_id = self.env.ref('sost_pricelist_mail.template_pricelist_mail')
		lang = self.env.context.get('lang')
		ctx = {
			'default_model': 'product.pricelist',
			'default_res_id': self.ids[0],
			'default_use_template': True,
			'default_template_id': mail_template_id.id,
			'default_composition_mode': 'comment',
			'force_email': True,
			'model_description': self.with_context(lang=lang).name,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(False, 'form')],
			'view_id': False,
			'target': 'new',
			'context': ctx,
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




