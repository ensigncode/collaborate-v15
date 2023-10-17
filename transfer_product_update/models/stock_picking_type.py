# -*- coding: utf-8 -*-

from odoo import models,fields,api

class StockPickingType(models.Model):
	_inherit = "stock.picking.type"

	is_pick_type = fields.Boolean(string="Is Pick Type")

class StockPicking(models.Model):
	_inherit = "stock.picking"

	is_pick_type = fields.Boolean(string="Is Pick Type",related="picking_type_id.is_pick_type",store=True)