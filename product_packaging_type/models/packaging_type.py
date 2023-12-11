from odoo import models,fields,api

class PackagingType(models.Model):
    _name = 'packaging.type'
    _description = 'MRP State'

    name = fields.Char(string="Name")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    packaging_type_id = fields.Many2one('packaging.type',string="Packaging Type")
