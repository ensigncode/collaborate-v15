# -*- coding: utf-8 -*-

from odoo import models,fields,api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_cos_category = fields.Boolean(string="HU Category")
