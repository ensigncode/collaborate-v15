from odoo import api, models
from odoo.tools.misc import get_lang


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        current_lang = get_lang(self.env).code

        for vals in vals_list:
            vals['lang'] = current_lang

        return super(ResPartner, self).create(vals_list)
