from odoo import models,fields,api

class MRPState(models.Model):
    _name = 'mrp.state'
    _description = 'MRP State'

    name = fields.Char(string="Name")
    state = fields.Selection([('draft','Draft'),
                            ('confirmed','Confirm'),
                            ('done','Done')],string="State")
