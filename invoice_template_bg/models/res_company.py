# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    
    report_template_id = fields.Many2one(
        string='Report',
        comodel_name='ir.actions.report',
        domain=[('model','=','account.move')]
    )
