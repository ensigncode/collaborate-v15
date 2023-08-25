odoo.define('pos_split_refund_discount.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const { parse } = require('web.field_utils');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener, useAutofocus } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');

    const RefundDiscountSplit = TicketScreen => class extends TicketScreen {

        getDiscountAmount(program, amount) {
            var discountAmount = (amount * program.discount_percentage) / 100.0;
            return discountAmount
        }

        // @Override
        _getToRefundDetail(orderline) {
            if (orderline.id in this.env.pos.toRefundLines) {
                return this.env.pos.toRefundLines[orderline.id];
            } else {
                var discount_line = _.filter(this.props.destinationOrder.pos.coupon_programs_by_id, function(coupon){
                    return coupon.discount_line_product_id[0] == orderline.product.id;
                });
                const customer = orderline.order.get_client();
                const orderPartnerId = customer ? customer.id : false;
                const newToRefundDetail = {
                    qty: 0,
                    orderline: {
                        isDiscountLine: discount_line.length > 0 ? discount_line : [],
                        id: orderline.id,
                        productId: orderline.product.id,
                        price: orderline.price,
                        qty: orderline.quantity,
                        refundedQty: orderline.refunded_qty,
                        orderUid: orderline.order.uid,
                        orderBackendId: orderline.order.backendId,
                        orderPartnerId,
                        tax_ids: orderline.get_taxes().map(tax => tax.id),
                        discount: orderline.discount,
                    },
                    destinationOrderUid: false,
                };
                this.env.pos.toRefundLines[orderline.id] = newToRefundDetail;
                return newToRefundDetail;
            }
        }

        // @Override
        _onUpdateSelectedOrderline({ detail }) {
            const buffer = detail.buffer;
            const order = this.getSelectedSyncedOrder();
            if (!order) return NumberBuffer.reset();

            const selectedOrderlineId = this.getSelectedOrderlineId();
            const orderline = order.orderlines.models.find((line) => line.id == selectedOrderlineId);
            if (!orderline) return NumberBuffer.reset();

            const toRefundDetail = this._getToRefundDetail(orderline);
            // When already linked to an order, do not modify the to refund quantity.
            if (toRefundDetail.destinationOrderUid) return NumberBuffer.reset();

            const refundableQty = toRefundDetail.orderline.qty - toRefundDetail.orderline.refundedQty;
            if (refundableQty <= 0) return NumberBuffer.reset();

            if (buffer == null || buffer == '') {
                toRefundDetail.qty = 0;
            } else {
                const quantity = Math.abs(parse.float(buffer));
                if (quantity > refundableQty) {
                    NumberBuffer.reset();
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Maximum Exceeded'),
                        body: _.str.sprintf(
                            this.env._t(
                                'The requested quantity to be refunded is higher than the ordered quantity. %s is requested while only %s can be refunded.'
                            ),
                            quantity,
                            refundableQty
                        ),
                    });
                } else {
                    toRefundDetail.qty = quantity;
                }
            }
            var toRefundLines = this.env.pos.toRefundLines;

             var amountTotal = _.map(_.filter(
                    Object.values(this.env.pos.toRefundLines), v => v.orderline.isDiscountLine.length == 0)
                    , v => v.orderline.price * v.qty).reduce((a, b) => a + b, 0);
            for (let k in toRefundLines) {
               if (toRefundLines[k].orderline.isDiscountLine.length > 0){
                    var discount_amount = this.getDiscountAmount(toRefundLines[k].orderline.isDiscountLine[0], amountTotal);
                    toRefundLines[k].orderline.price = -1*discount_amount;
               }
            }
            this.render();
        }
        _getSearchFields() {
            return Object.assign({}, super._getSearchFields(), {
                PHONE_NUMBER: {
                    repr: (order) => order.get_client_name(),
                    displayName: this.env._t('Phone'),
                    modelField: 'partner_id.phone',
                }
            });
        }

    };

    Registries.Component.extend(TicketScreen, RefundDiscountSplit);

    return TicketScreen;
});
