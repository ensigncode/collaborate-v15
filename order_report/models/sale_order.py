# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPort(models.Model):
    _name = 'res.port'
    _description = 'Res Port'

    name = fields.Char(string="Name")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking = fields.Char('Booking')
    truck_nm = fields.Char('Truck')
    port_id = fields.Many2one('res.port',string="Port")
    freight = fields.Float(string="Freight")