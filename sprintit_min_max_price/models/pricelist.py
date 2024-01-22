# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

from odoo import models, _


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def get_products_price(self, products, quantities, partners, date=False, uom_id=False):
        """ For a given pricelist, return price for products
        Returns: dict{product_id: product price}, in the given pricelist """
        self.ensure_one()
        sale_pricelist_min_price = self.env['ir.config_parameter'].sudo().get_param('sale.sale_pricelist_min_price')
        sale_pricelist_max_price = self.env['ir.config_parameter'].sudo().get_param('sale.sale_pricelist_max_price')
        if sale_pricelist_min_price == False and sale_pricelist_max_price == False:
            return super(Pricelist, self).get_products_price(products, quantities, partners, date=date, uom_id=uom_id)
        pricelist_obj = self.env['product.pricelist']
        pricelist_ids = final_pricelists = self.ids
        while (pricelist_ids):
            self._cr.execute("""SELECT distinct item.base_pricelist_id 
             FROM product_pricelist_item AS item 
             WHERE item.applied_on = '3_global' 
             AND item.base = 'pricelist' 
             AND item.base_pricelist_id IS NOT NULL 
             AND pricelist_id in (%s)""" % (','.join(str(i) for i in pricelist_ids)))
            pricelist_ids = [x[0] for x in self._cr.fetchall()]
            final_pricelists.extend(pricelist_ids)
        pricelists = pricelist_obj.browse(final_pricelists)
        for product_id, res_tuple in pricelists._compute_price_rule_multi(
                list(zip(products, quantities, partners)),
                date=date,
                uom_id=uom_id
        ).items():
            price_values = 0
            for item in res_tuple.values():
                if not price_values:
                    price_values = item[0]
                else:
                    if sale_pricelist_min_price:
                        price_values = min(price_values, item[0])
                    elif sale_pricelist_max_price:
                        price_values = max(price_values, item[0])
        result = {
            product_id: price_values
        }
        return result
