# -*- coding: utf-8 -*-

from odoo import models,fields,api

class MRPStatus(models.Model):
    _name = 'mrp.status'
    _description = 'MRP Status'

    name = fields.Char(string="Name")
    state = fields.Selection([('draft','Draft'),
                            ('confirmed','Confirm'),
                            ('done','Done')],string="State")
