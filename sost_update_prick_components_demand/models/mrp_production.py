# -*- coding: utf-8 -*-

from odoo import _, api,fields, models


class MRPProduction(models.Model):
	_inherit = "mrp.production"

	production_picking_ids = fields.One2many('stock.picking','raw_production_id')

	def action_confirm(self):
		res = super(MRPProduction,self).action_confirm()
		if self.picking_ids:
			for picking in self.picking_ids:
				picking.raw_production_id = self.id
		return res


	def write(self,vals):
		res = super(MRPProduction,self).write(vals)
		if 'qty_producing' in vals:
			for production in self:
				done_picking_id =  production.production_picking_ids.filtered(lambda x:x.state == 'done')
				picking_ids = production.production_picking_ids.filtered(lambda x:x.state != 'done')
				if done_picking_id:
					picking_ids = picking_ids.filtered(lambda x:x.id > done_picking_id.id)
				if picking_ids:
					for picking in picking_ids:
						picking.move_update_qty()
		return res
