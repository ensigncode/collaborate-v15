# -*- coding: utf-8 -*-

from odoo import models,fields,api

class Users(models.Model):
	_inherit = "res.users"

	order_warehouse_ids = fields.Many2many('stock.warehouse',string="Warehouse")
