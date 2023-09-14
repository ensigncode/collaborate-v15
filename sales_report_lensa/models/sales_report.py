from odoo import fields, models

class PivotInheritReport(models.Model):
    _inherit = "sale.report"

    margin_per = fields.Float(string='Margin %')
    total_payment = fields.Float(string='Total Payment')

    # def _select_sale(self,fields=None):
    #     res = super(PivotInheritReport,self)._select_sale(fields)
    #     res +=  """, (SUM(l.margin)/s.amount_untaxed)*100 AS margin_per,
    #                 case when pol.price_subtotal is not null then pol.price_subtotal else 0.0 end
    #                  +
    #                 case when (select sum(amount) from account_payment as ap where move_id in (select id from account_move where ref=am.name)) is not null then (select sum(amount) from account_payment as ap where move_id in (select id from account_move where ref=am.name)) else 0.0 end AS total_payment
    #             """
    #     return res
    
    # def _from_sale(self, from_clause=''):
    #     res = super(PivotInheritReport,self)._from_sale(from_clause)
    #     res += """  
    #             JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = l.id
    #             JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
    #             JOIN account_move am ON am.id = aml.move_id                  
    #             JOIN pos_order_line pol ON l.id = pol.sale_order_origin_id
    #         """
    #     return res


    def _select_sale(self,fields=None):
        res = super(PivotInheritReport,self)._select_sale(fields)
        res +=  """, (SUM(l.margin)/s.amount_untaxed)*100 AS margin_per,
                    case when (select sum(amount) from account_payment as ap where move_id in (select id from account_move where ref=am.name)) is not null then (select sum(amount) from account_payment as ap where move_id in (select id from account_move where ref=am.name)) else 0.0 end AS total_payment
                """
        return res
    
    def _select_pos(self,fields=None):
        fields['margin_percent'] = ', (SUM(l.price_subtotal - COALESCE(l.total_cost,0) / CASE COALESCE(pos.currency_rate, 0) WHEN 0 THEN 1.0 ELSE pos.currency_rate END) / SUM(l.price_subtotal))*100 AS margin_per'
        fields['total_payment'] = ', (SELECT sum(amount) FROM account_payment AS ap WHERE move_id IN (SELECT id FROM account_move WHERE ref=am.name)) AS total_payment'
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

    # def _group_by_sale(self, groupby=''):
    #     res = super(PivotInheritReport,self)._group_by_sale(groupby)
    #     res += """, s.margin_percent, am.id, am.name, s.amount_untaxed, pol.price_subtotal"""
    #     return res

    def _group_by_sale(self, groupby=''):
        res = super(PivotInheritReport,self)._group_by_sale(groupby)
        res += """, s.margin_percent, am.id, am.name, s.amount_untaxed"""
        return res
    
    def _group_by_pos(self):
        res = super(PivotInheritReport,self)._group_by_pos()
        res += """, am.name"""
        return res