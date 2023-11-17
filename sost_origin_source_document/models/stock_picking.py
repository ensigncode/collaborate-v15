# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	source_document = fields.Char(string="Source Document")
	orig_source_document = fields.Char(string="Original Source Document")
