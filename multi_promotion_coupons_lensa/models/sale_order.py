# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date


class SaleOrder(models.Model):
    _inherit = "sale.order"

    code_promo_program_ids = fields.Many2many(
        comodel_name='coupon.program', 
        relation='order_coupon_program_rel',
        string='Applied Promo Programs'
        )
    
    def _create_reward_line(self, program):
        self.with_context(program_id=program).write({'order_line': [(0, False, value) for value in self._get_reward_line_values(program)]})

    def _get_reward_values_percentage_amount(self, program):
        # Invalidate multiline fixed_price discount line as they should apply after % discount
        fixed_price_products = self._get_applied_programs().filtered(
            lambda p: p.discount_type == 'fixed_amount'
        ).mapped('discount_line_product_id')

        # Comment this line for apply multiple coupon in order. Sometime odoo changed applied coupon line values. 
        # self.order_line.filtered(lambda l: l.product_id in fixed_price_products).write({'price_unit': 0})

        reward_dict = {}
        lines = self._get_paid_order_lines()
        amount_total = sum([any(line.tax_id.mapped('price_include')) and line.price_total or line.price_subtotal
                            for line in self._get_base_order_lines(program)])
        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line()
            if line:
                discount_line_amount = min(line.price_reduce * (program.discount_percentage / 100), amount_total)
                if discount_line_amount:
                    taxes = self.fiscal_position_id.map_tax(line.tax_id)

                    reward_dict[line.tax_id] = {
                        'name': _("Discount: %s", program.name),
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                        'product_uom_qty': 1.0,
                        'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in taxes],
                    }
        elif program.discount_apply_on in ['specific_products', 'on_order']:
            if program.discount_apply_on == 'specific_products':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['coupon.program'].search([('reward_type', '=', 'product'), ('reward_product_id', 'in', program.discount_specific_product_ids.ids)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.product_id in (program.discount_specific_product_ids | free_product_lines))

            # when processing lines we should not discount more than the order remaining total
            currently_discounted_amount = 0
            for line in lines:
                discount_line_amount = min(self._get_reward_values_discount_percentage_per_line(program, line), amount_total - currently_discounted_amount)

                if discount_line_amount:

                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]['price_unit'] -= discount_line_amount
                    else:
                        taxes = self.fiscal_position_id.map_tax(line.tax_id)

                        reward_dict[line.tax_id] = {
                            'name': _(
                                "Discount: %(program)s - On product with following taxes: %(taxes)s",
                                program=program.name,
                                taxes=", ".join(taxes.mapped('name')),
                            ),
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                            'product_uom_qty': 1.0,
                            'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_id': [(4, tax.id, False) for tax in taxes],
                        }
                        currently_discounted_amount += discount_line_amount

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty','price_unit')
    def _onchange_reward_price_unit(self):
        for rec in self:
            if not rec.is_reward_line:
                non_reward_line_total = sum(self.search([('order_id','=',self.order_id._origin.id),('is_reward_line','=',False),('id','!=',rec._origin.id)]).mapped('price_subtotal'))
                line_subtotal = rec.price_subtotal
                non_reward_line_total += line_subtotal
                for reward_line in self.order_id.order_line.filtered(lambda line:line.is_reward_line):
                    program_id = self.env['coupon.program'].search([('discount_line_product_id', '=', reward_line.product_id.id)],limit=1)
                    discounted_price_unit = -non_reward_line_total * (program_id.discount_percentage / 100)
                    reward_line._origin.price_unit = discounted_price_unit
                    non_reward_line_total += discounted_price_unit


    def read_converted(self):
        field_names = ["product_id", "name", "price_unit", "product_uom_qty", "tax_id", "qty_delivered",
                       "is_reward_line", "qty_invoiced", "discount", "qty_to_invoice", "price_total"]
        results = []
        for sale_line in self:
            if sale_line.product_type:
                product_uom = sale_line.product_id.uom_id
                sale_line_uom = sale_line.product_uom
                item = sale_line.read(field_names)[0]
                if sale_line.product_id.tracking != 'none':
                    item['lot_names'] = sale_line.move_ids.move_line_ids.lot_id.mapped('name')
                if product_uom == sale_line_uom:
                    results.append(item)
                    continue
                item['product_uom_qty'] = self._convert_qty(sale_line, item['product_uom_qty'], 's2p')
                item['qty_delivered'] = self._convert_qty(sale_line, item['qty_delivered'], 's2p')
                item['qty_invoiced'] = self._convert_qty(sale_line, item['qty_invoiced'], 's2p')
                item['qty_to_invoice'] = self._convert_qty(sale_line, item['qty_to_invoice'], 's2p')
                item['price_unit'] = sale_line_uom._compute_price(item['price_unit'], product_uom)
                results.append(item)

            elif sale_line.display_type == 'line_note':
                if results:
                    results[-1]['customer_note'] = sale_line.name
        return results
    
    # Calculate reward line price unit for apply discounted price.
    def update_reward_line_price_unit(self):
        if self._context.get('unlink'):
            order_line = self
            self = self.order_id
            product_order_line_price_sum = sum(self.order_line.filtered(lambda line: not line.is_reward_line and line.id != order_line.id).mapped('price_subtotal'))
        elif self._context.get('create'):
            if self._context.get('price_unit'):
                product_price_unit = self._context.get('price_unit') 
            self = self._context.get('order')
            product_order_line_price_sum = sum(self.order_line.filtered(lambda line: not line.is_reward_line).mapped('price_subtotal'))
            if product_price_unit:
                product_order_line_price_sum += product_price_unit 
        for line in self.order_line.filtered(lambda line: line.is_reward_line):
            program_id = self.env['coupon.program'].search([('discount_line_product_id', '=', line.product_id.id)],limit=1)
            line.price_unit = -product_order_line_price_sum * (program_id.discount_percentage / 100)
            product_order_line_price_sum += -product_order_line_price_sum * (program_id.discount_percentage / 100)

    def unlink(self):
        related_program_lines = self.env['sale.order.line']
        # Reactivate coupons related to unlinked reward line
        for line in self.filtered(lambda line: line.is_reward_line):
            coupons_to_reactivate = line.order_id.applied_coupon_ids.filtered(
                lambda coupon: coupon.program_id.discount_line_product_id == line.product_id
            )
            coupons_to_reactivate.write({'state': 'new'})
            line.order_id.applied_coupon_ids -= coupons_to_reactivate
            # Remove the program from the order if the deleted line is the reward line of the program
            # And delete the other lines from this program (It's the case when discount is split per different taxes)
            related_program = self.env['coupon.program'].search([('discount_line_product_id', '=', line.product_id.id)])
            if related_program:
                line.order_id.no_code_promo_program_ids -= related_program
                line.order_id.code_promo_program_id -= related_program
                line.order_id.code_promo_program_ids -= related_program
                related_program_lines |= line.order_id.order_line.filtered(lambda l: l.product_id.id == related_program.discount_line_product_id.id) - line
        for li in self:
            li.with_context(unlink=True).update_reward_line_price_unit()
        return super(SaleOrderLine, self | related_program_lines).unlink()
    
    @api.model_create_multi
    def create(self,vals):
        for val in vals:
            if val.get('is_reward_line'):
                if val.get('order_id'):
                    sale_order = self.env['sale.order'].browse(val.get('order_id'))
                    product_line_total = sum(sale_order.order_line.filtered(lambda line:not line.is_reward_line).mapped('price_subtotal'))
                    is_reward_lines = sale_order.order_line.filtered(lambda line: line.is_reward_line)
                    for reward in is_reward_lines:
                        product_line_total += reward.price_unit
                    if self._context.get('program_id'):
                        price_unit = product_line_total * (self._context.get('program_id').discount_percentage / 100)
                    val.update({'price_unit':-price_unit})
            else:
                self.with_context(create=True,price_unit=val.get('price_unit'),order=self.env['sale.order'].browse(val.get('order_id'))).update_reward_line_price_unit()

        return super(SaleOrderLine,self).create(vals)
