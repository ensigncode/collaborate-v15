from odoo import fields, models

class PivotInheritReport(models.Model):
    _inherit = "sale.report"

    pos_cashed_in = fields.Float(string='Cashed in')

    def _select_additional_fields(self, fields):
        fields['pos_cashed_in'] = ", sum(l.pos_cashed_in) as pos_cashed_in"
        return super()._select_additional_fields(fields)
