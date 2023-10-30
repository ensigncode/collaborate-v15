# -*- coding: utf-8 -*-

from odoo import models,fields,api, _

class ProductPutawayRule(models.TransientModel):
    _name = 'product.putaway.rule'
    _description = 'Product Putaway Rule'

    po_id = fields.Many2one('purchase.order',string="Purchase")
    product_putaway_rule_line_ids = fields.One2many('product.putaway.rule.line','rule_id')

    def action_confirm(self):
        rule_ids = []
        for line in self.product_putaway_rule_line_ids:
            if line.location_out_id:
                vals = {
                        'product_id':line.product_id.id,
                        'storage_category_id':line.storage_category_id.id,
                        'location_out_id':line.location_out_id.id if line.location_out_id else False,
                        'location_in_id':line.location_in_id.id if line.location_in_id else False,
                    }
                rule_id = self.env['stock.putaway.rule'].create(vals)
                rule_ids.append(rule_id.id)

        self.po_id.button_confirm()
        return True

class ProductPutawayRuleLine(models.TransientModel):
    _name = 'product.putaway.rule.line'
    _description = 'Product Putaway Rule Line'

    operation_type = fields.Selection([('existing','Select One Of the Existing'),
                                    ('manually','Define the putaway rule manually later')],string="Type",default="existing")
    location_out_id = fields.Many2one('stock.location',string="Substore Location")
    location_in_id = fields.Many2one('stock.location',string="Arrive Location")
    storage_category_id = fields.Many2one('stock.storage.category',string="Stock Category")
    product_id = fields.Many2one('product.product',string="Product")
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company)
    rule_id = fields.Many2one('product.putaway.rule',string="Rule Id")
    fix_location = fields.Boolean(string="Location Fix")


