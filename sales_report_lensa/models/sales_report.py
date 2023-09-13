from odoo import fields, models

class PivotInheritReport(models.Model):
    _inherit = "sale.report"

    margin_per = fields.Float(string='Margin %')
    total_payment = fields.Float(string='Total Payment')

    def _select_sale(self,fields=None):
        res = super(PivotInheritReport,self)._select_sale(fields)
        res +=  """, SUM(l.margin_percent)*100 AS margin_per, 
                    (select sum(amount) from account_payment as ap where move_id in (select id from account_move where ref=am.name)) AS total_payment
                """
        return res
    
    def _select_pos(self,fields=None):
        fields['margin_percent'] = ', (SUM(l.price_subtotal - COALESCE(l.total_cost,0) / CASE COALESCE(pos.currency_rate, 0) WHEN 0 THEN 1.0 ELSE pos.currency_rate END) / SUM(l.price_subtotal))*100 AS margin_per'
        fields['total_payment'] = ', SUM(pop.amount) AS total_payment'
        # fields['total_payment'] = ', (select sum(amount) from account_payment as ap where move_id in (select id from account_move where ref=am.name)) AS total_payment'
        return super(PivotInheritReport,self)._select_pos(fields)

    def _from_sale(self, from_clause=''):
        res = super(PivotInheritReport,self)._from_sale(from_clause)
        res += """
                    JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = l.id
                    JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
                    JOIN account_move am ON am.id = aml.move_id
                """
        return res
    
    def _from_pos(self):
        res = super(PivotInheritReport,self)._from_pos()
        res += """
                    JOIN pos_payment pop ON pop.pos_order_id = pos.id
                    JOIN account_move am ON am.id = pop.account_move_id
                """
        return res

    def _group_by_sale(self, groupby=''):
        res = super(PivotInheritReport,self)._group_by_sale(groupby)
        res += """, s.margin_percent, am.id, am.name"""
        return res
    
    def _group_by_pos(self):
        res = super(PivotInheritReport,self)._group_by_pos()
        res += """, am.name"""
        return res
