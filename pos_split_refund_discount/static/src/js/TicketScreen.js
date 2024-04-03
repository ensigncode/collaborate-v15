odoo.define('pos_split_refund_discount.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const { parse } = require('web.field_utils');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener, useAutofocus } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');

    const RefundDiscountSplit = TicketScreen => class extends TicketScreen {

        getDiscountAmount2(program, amount) {
            var discountAmount = (amount * program.discount_percentage) / 100.0;
            return discountAmount
        }

        // @Override
        _getToRefundDetail2(orderline) {
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
                        isDiscountLine: discount_line && discount_line.length > 0 ? discount_line : [],
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
        _onUpdateSelectedOrderline2({ detail }) {
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
                    Object.values(this.env.pos.toRefundLines), v => v.orderline.isDiscountLine && v.orderline.isDiscountLine.length == 0)
                    , v => v.orderline.price * v.qty).reduce((a, b) => a + b, 0);
            for (let k in toRefundLines) {
               if (toRefundLines[k].orderline.isDiscountLine && toRefundLines[k].orderline.isDiscountLine.length > 0){
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

        _onClickOrderline({ detail: orderline }) {
            if (orderline && orderline.is_program_reward) {
                return;
            }
            return super._onClickOrderline(...arguments);
        }

        async _onDoRefund() {
            const self = this;
            const order = this.getSelectedSyncedOrder();
            if (!order) {
                this._state.ui.highlightHeaderNote = !this._state.ui.highlightHeaderNote;
                return this.render();
            }

            if (this._doesOrderHaveSoleItem(order)) {
                this._prepareAutoRefundOnOrder(order);
            }

            const customer = order.get_client();

            const allToRefundDetails = this._getRefundableDetails(customer)
            if (allToRefundDetails.length == 0) {
                this._state.ui.highlightHeaderNote = !this._state.ui.highlightHeaderNote;
                return this.render();
            }

            // The order that will contain the refund orderlines.
            // Use the destinationOrder from props if the order to refund has the same
            // customer as the destinationOrder.
            const destinationOrder = this._setDestinationOrder(this.props.destinationOrder, customer);
            //Add a check too see if the fiscal position exist in the pos
            if (order.fiscal_position_not_found) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Fiscal Position not found'),
                    body: this.env._t('The fiscal position used in the original order is not loaded. Make sure it is loaded by adding it in the pos configuration.')
                });
                return;
            }

            // Add orderline for each toRefundDetail to the destinationOrder.
            for (const refundDetail of allToRefundDetails) {
                const product = this.env.pos.db.get_product_by_id(refundDetail.orderline.productId);
                const options = this._prepareRefundOrderlineOptions(refundDetail);
                await destinationOrder.add_product(product, options);
                refundDetail.destinationOrderUid = destinationOrder.uid;
            }

            destinationOrder.fiscal_position = order.fiscal_position;
            // Set the customer to the destinationOrder.
            if (customer && !destinationOrder.get_client()) {
                destinationOrder.set_client(customer);
                destinationOrder.updatePricelist(customer);
            }

            /*const { canDoRefund, linesToAdd } = await this.rpc({
                model: 'pos.order',
                method: 'prepare_promo_refund_lines',
                args: [[order.backendId], allToRefundDetails],
                context: this.env.session.user_context,
            });*/

            let o_lines = order.get_orderlines();
            let o_lines_non_promo = _.filter(o_lines, function (l) { return l.price >= 0 });
            let o_lines_promo = _.filter(o_lines, function (l) { return l.price < 0 });

            if (o_lines_promo && o_lines_promo.length > 0) {
                let d_lines = destinationOrder.get_orderlines();
                let d_lines_non_promo = _.filter(d_lines, function (l) { return l.price < 0 });
                let d_lines_promo = _.filter(d_lines, function (l) { return l.price >= 0 });

                // Check partial/full order refund
                var is_partial_refund = false;
                if (allToRefundDetails.length == o_lines_non_promo.length) {
                    for (const refundDetail of allToRefundDetails) {
                        if (refundDetail.qty < refundDetail.orderline.qty) {
                            is_partial_refund = true
                        }
                    }
                }
                // if full return then add lines to refund order
                if (!is_partial_refund) {
                    for (const promoDetail of o_lines_promo) {
                        const product = this.env.pos.db.get_product_by_id(promoDetail.product.id);
                        const options = this._prepareRefundOrderlineOptions({'qty': promoDetail.quantity, 'orderline': promoDetail});
                        await destinationOrder.add_product(product, options);
                        promoDetail.destinationOrderUid = destinationOrder.uid;
                    }
                }
                // if partial refund then handle cases
                else {
                    var temp_order = this.env.pos.add_new_order({ silent: true });
                    temp_order.fiscal_position = order.fiscal_position;
                    if (customer) {
                        temp_order.set_client(customer);
                        temp_order.updatePricelist(customer);
                    }
                    for (const orderline of o_lines_non_promo) {
                        var remaining_qty = orderline.quantity;
                        for (const refundDetail of allToRefundDetails) {
                            if (refundDetail.orderline.id == orderline.id) {
                                remaining_qty = remaining_qty - refundDetail.qty;
                            }
                        }
                        if (remaining_qty > 0) {
                            const product = this.env.pos.db.get_product_by_id(orderline.product.id);
                            const options = this._prepareRefundOrderlineOptions({'qty': remaining_qty, 'orderline': orderline});
                            options['quantity'] = remaining_qty;
                            options['refunded_orderline_id'] = false;
                            temp_order.add_product(product, options);
                        }
                    }

                    let applied_program_ids = [];
                    const promoPrograms = self.env.pos.promo_programs.filter(
                        (program) => order.applied_program_ids.includes(program.id)
                    );
                    for (const promoProgram of promoPrograms) {
                        const { successful, reason } = await temp_order._checkProgramRules(promoProgram);
                        if (successful) {
                            applied_program_ids.push(promoProgram.id);
                        }
                    }

                    if (applied_program_ids && order.applied_program_ids) {
                        var diff1 = _.difference(applied_program_ids, order.applied_program_ids);
                        var diff2 = _.difference(order.applied_program_ids, applied_program_ids);
                        if (diff1.length || diff2.length) {
                            const { confirmed } = await self.showPopup('ConfirmPopup', {
                                title: self.env._t('Refund Order'),
                                body: self.env._t(
                                    'The discount parameters are not met anymore. Refund the entire order!'
                                ),
                                confirmText: self.env._t('Yes'),
                                cancelText: self.env._t('No')
                            });
                            if (confirmed) {
                                for (const line_idx in o_lines) {
                                    var line = o_lines[line_idx];
                                    var found_line = false;
                                    for (const dline_idx in d_lines) {
                                        var dline = d_lines[dline_idx];
                                        if (dline.refunded_orderline_id == line.id) {
                                            found_line = dline;
                                        }
                                    }
                                    if (found_line) {
                                        found_line.set_quantity(line.quantity * -1);
                                        found_line.set_unit_price(line.price);
                                    } else {
                                        const product = this.env.pos.db.get_product_by_id(line.product.id);
                                        const options = this._prepareRefundOrderlineOptions({'qty': line.quantity, 'orderline': line});
                                        await destinationOrder.add_product(product, options);
                                        line.destinationOrderUid = destinationOrder.uid;
                                    }
                                }
                            } else {
                                destinationOrder.destroy({'reason':'abandon'});
                            }
                        } else {
                            var total = destinationOrder.get_total_with_tax();
                            var order_total = _.reduce(o_lines_non_promo.map(function (l) { return l.get_price_with_tax()}), function (a, b) { return a + b });
                            for (const promo_line of o_lines_promo) {
                                const promoProgram = self.env.pos.promo_programs.find(
                                    (program) => program.id == promo_line.program_id
                                );
                                if (promoProgram.reward_type == 'discount' && promoProgram.discount_type == 'percentage') {
                                    const product = this.env.pos.db.get_product_by_id(promo_line.product.id);
                                    const options = this._prepareRefundOrderlineOptions({'qty': promo_line.quantity, 'orderline': promo_line});
                                    options['price'] = total * promoProgram.discount_percentage / 100;
                                    destinationOrder.add_product(product, options);
                                }
                                if (promoProgram.reward_type == 'discount' && promoProgram.discount_type == 'fixed_amount') {
                                    const product = this.env.pos.db.get_product_by_id(promo_line.product.id);
                                    const options = this._prepareRefundOrderlineOptions({'qty': promo_line.quantity, 'orderline': promo_line});
                                    options['price'] = (promo_line.price / order_total) * total * -1;
                                    destinationOrder.add_product(product, options);
                                }
                            }
                        }
                    }
                    temp_order.destroy({'reason':'abandon'});
                }
            }

            this._onCloseScreen();
        }

    };

    Registries.Component.extend(TicketScreen, RefundDiscountSplit);

    return TicketScreen;
});
