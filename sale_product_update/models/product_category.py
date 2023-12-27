# -*- coding: utf-8 -*-

from odoo import models,fields,api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_cos_category = fields.Boolean(string="HU Category")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_cos_product = fields.Boolean(string="HU Category",related="categ_id.is_cos_category",store=True)

    @api.model
    def _get_fields_stock_barcode(self):
        return ['barcode', 'default_code', 'detailed_type', 'tracking', 'display_name', 'uom_id','is_cos_product']
