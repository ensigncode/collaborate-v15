# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, time
from odoo.exceptions import UserError


class MRPReport(models.TransientModel):
    _inherit = "mrp.report"

    packaging_type_id = fields.Many2one('packaging.type',string="Packaging Type",related="product_id.product_tmpl_id.packaging_type_id")

