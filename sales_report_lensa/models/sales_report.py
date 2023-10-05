from odoo import fields, models


class PivotInheritReport(models.Model):
	_inherit = "sale.report"

	margin_per = fields.Float(string='Margin %')
	total_payment = fields.Float(string='Total Payment')
	brand_id = fields.Many2one('product.brand', string="Brand")

	def _select_sale(self, fields=None):
		res = super(PivotInheritReport, self)._select_sale(fields)
		res += """, (SUM(l.margin)/s.amount_untaxed)*100 AS margin_per,COALESCE(py.amount,0) AS total_payment, t.brand_id AS brand_id """
		return res

	def _select_pos(self, fields=None):
		fields[
			'margin_percent'] = ', (SUM(l.price_subtotal - COALESCE(l.total_cost,0) / CASE COALESCE(pos.currency_rate, 0) WHEN 0 THEN 1.0 ELSE pos.currency_rate END) / SUM(l.price_subtotal))*100 AS margin_per'
		fields[
			'total_payment'] = ', (SELECT sum(amount) FROM account_payment AS ap WHERE move_id IN (SELECT id FROM account_move WHERE ref=am.name)) AS total_payment'
		fields['brand_id'] = ', t.brand_id AS brand_id'
		return super(PivotInheritReport, self)._select_pos(fields)

	def _from_sale(self, from_clause=''):
		res = super(PivotInheritReport, self)._from_sale(from_clause)
		res += """
                    JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = l.id
                    FULL JOIN pos_order_line pol ON pol.sale_order_line_id = l.id
					FULL JOIN pos_order as po ON pol.order_id = po.id
					FULL JOIN pos_payment AS py ON py.pos_order_id = po.id
                """
		return res

	def _from_pos(self):
		res = super(PivotInheritReport, self)._from_pos()
		res += """
                    JOIN pos_payment pop ON pop.pos_order_id = pos.id
                    JOIN account_move am ON am.id = pop.account_move_id
                """
		return res

	def _group_by_sale(self, groupby=''):
		res = super(PivotInheritReport, self)._group_by_sale(groupby)
		res += """, s.margin_percent, s.amount_untaxed, py.amount, t.brand_id"""
		return res

	def _group_by_pos(self):
		res = super(PivotInheritReport, self)._group_by_pos()
		res += """, am.name, t.brand_id"""
		return res
