# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request


class ProductScanController(http.Controller):

	@http.route('/scan_product', type='http', auth='user', website=True)
	def scan_product_to_get_price(self, **kw):
		"""
			Open to template to scan product on the website
		"""
		return request.render('web_product_scanner.scan_product_barcode', {})

	@http.route('/fetch_product/<string:barcode>', type='json', auth='user')
	def fetch_product_to_get_price(self, barcode, **kw):
		"""
			Open to template to scan product on the website
		"""
		if not barcode:
			return "In order to fetch the product's data, please scan the barcode."
		barcode_product = request.env['product.product'].sudo().search([('barcode', '=', barcode.strip())], limit=1)
		if barcode_product:
			return {
				"product_name": barcode_product.display_name,
				"product_price": f"{barcode_product.lst_price} {request.env.company.currency_id.symbol}",
				"product_image": f"/web/image/product.product/{barcode_product.id}/image_1920",
				"product_barcode": barcode_product.barcode,
			}
		else:
			return f"Barcode: {barcode} doesn't exists in the product's catalog, please check the barcode or scan another."
