from odoo import fields, models


class PivotInheritReport(models.Model):
	_inherit = "sale.report"

	margin_per = fields.Float(string='Margin %')
	total_payment = fields.Float(string='Total Payment')
	brand_id = fields.Many2one('product.brand', string="Brand")

	def _select_sale(self, fields=None):
		res = super(PivotInheritReport, self)._select_sale(fields)
		res += """, (SUM(l.margin)/COALESCE(NULLIF(s.amount_untaxed, 0), 1))*100 AS margin_per """
		return res

	def _select_pos(self, fields=None):
		fields['margin_per'] = ', 0 AS margin_per'
		return super(PivotInheritReport, self)._select_pos(fields)
