# -*- coding: utf-8 -*-

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    gift_card_details = fields.Text()
