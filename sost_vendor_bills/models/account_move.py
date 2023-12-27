# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	option_type = fields.Selection([('is_modified','Modified'),('is_added','Added')],string="Type")
	