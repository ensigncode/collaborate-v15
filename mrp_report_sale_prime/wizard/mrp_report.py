from odoo import models,fields,api

class MRPReport(models.TransientModel):
    _inherit = "mrp.report.wizard"

    order_id = fields.Many2one('sale.order',related="mrp_id.order_id")
    client_order_ref =  fields.Char(string="Client Ref",related="mrp_id.order_id.client_order_ref")

