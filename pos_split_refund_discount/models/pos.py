# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def prepare_promo_refund_lines(self, refund_lines):
        print("self... ", self)
        print("refund_lines... ", refund_lines)
        return False, refund_lines

    def _export_for_ui(self, order):
        data = super(PosOrder, self)._export_for_ui(order)
        data["applied_program_ids"] = order.applied_program_ids.ids
        return data


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def _export_for_ui(self, orderline):
        data = super(PosOrderLine, self)._export_for_ui(orderline)
        data['is_program_reward'] = orderline.is_program_reward
        data['program_id'] = orderline.program_id.id
        return data
