# -*- coding: utf-8 -*-

from odoo import models,fields,api

class UpdatePutawayRule(models.Model):
    _name = 'update.putaway.rule'
    _description = 'Update Putaway Rule'

    operation_type = fields.Selection([('existing','Select One Of the Existing'),
                                    ('manually','Define the putaway rule manually later')],string="Type",default="manually")

    location_out_id = fields.Many2one('stock.location',string="Substore Location")
    location_in_id = fields.Many2one('stock.location',string="Arrive Location")
    product_id = fields.Many2one('product.product',string="Product")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
             default=lambda self: self.env.company)

    def action_confirm(self):
        if self.operation_type == "existing":
            vals = {
                'product_id':self.product_id.id,
                'location_out_id':self.location_out_id.id,
                'location_in_id':self.location_in_id.id,
            }
            putaway_rule_id = self.env['stock.putaway.rule'].create(vals)
        else:
            return {
                'name': 'Putaway Rule',
                'view_mode': 'form',
                'target': 'current',
                'res_model': 'stock.putaway.rule',
                'type': 'ir.actions.act_window',
            }
