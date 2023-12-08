# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, time
from odoo.exceptions import UserError

class MRPReport(models.TransientModel):
    _inherit = "mrp.report"

    order_id = fields.Many2one('sale.order',related="mrp.order_id")
    client_order_ref =  fields.Char(string="Client Ref",related="mrp.order_id.client_order_ref")

