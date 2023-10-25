# -*- coding: utf-8 -*-
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.website_sale.controllers.main import Website
from odoo.http import request


class WebsiteDataLayer(Website):

	@http.route('/shop/payment/track_payment/<int:sale_order_id>', type='json', auth="public", website=True)
	def shop_payment_get_status(self, sale_order_id, **post):
		order = request.env['sale.order'].sudo().browse(sale_order_id).exists()
		return {
			'currency': order.currency_id.code,
			'value': order.amount_untaxed,
			'tax': order.amount_tax,
			'shipping': 5.00,
			'affiliation': 'My online shop',
			'transaction_id': order.get_portal_last_transaction().display_name,
			'coupon': False,
			'items': [{
				'item_name': item.product_id.name,
				'item_id': item.product_id.id,
				'price': item.price_unit,
				'item_brand': False,
				'item_category': ', '.join(item.product_id.puclic_categ_ids.mapped('name')),
				'item_category2': False,
				'item_variant': item.product_id.product_template_attribute_value_ids.mapped('name'),
				'quantity': item.product_uom_qty,
				'item_coupon': False,
			} for item in order.order_line]
		}
