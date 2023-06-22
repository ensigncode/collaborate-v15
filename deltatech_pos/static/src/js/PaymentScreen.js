odoo.define("deltatech_pos.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");

    const Registries = require("point_of_sale.Registries");
    const {parse} = require("web.field_utils");

    // Var models = require("point_of_sale.models");
    var rpc = require("web.rpc");
    var ECRFile = require("deltatech_pos.ecr_file");

    const ECRPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            get_cash_value() {
                return 0.0;
            }

            async order_note() {
                var order = this.currentOrder;
                const orderNote = await this.showPopup("TextInputPopup", {title: "Note"});
                order.note = orderNote.payload;
            }

            cash_box_in() {
                this.click_cash_box_in_out("in");
            }

            cash_box_out() {
                this.click_cash_box_in_out("out");
            }

            async click_cash_box_in_out(type_operation) {
                var self = this;
                var value = this.get_cash_value(type_operation);

                var is_customer = await self.check_is_customer();

                if (!is_customer) {
                    return;
                }

                var title = "";
                var ref = "";
                if (type_operation === "in") {
                    title = this.env._t("Cash collection");
                    ref = self.env.pos.config.text_cash_in;
                } else {
                    title = this.env._t("Payment disposal");
                    ref = self.env.pos.config.text_cash_in;
                }

                // Var order = this.env.pos.get_order();
                var order = this.currentOrder;
                if (order.note) {
                    ref = ref + " " + order.note;
                }

//                const {confirmed, payload} = await this.showPopup("NumberPopup", {
//                    startingValue: value,
//                    title: title,
//                });
//
//                if (confirmed) {
                    var values = {
                        amount: order.get_total_with_tax(),
                        name: title,
                        partner_id: order.get_client().id,
                        ref: ref,
                    };
                    values.amount = Math.abs(values.amount);

                    if (type_operation === "out") {
                        values.amount = -values.amount;
                    }
                    var context = {
                        active_model: "pos.session",
                        active_ids: [window.posmodel.pos_session.id],
                    };
                    return rpc
                        .query({
                            model: "cash.box.out",
                            method: "create_and_run",
                            args: [values],
                            context: context,
                        })
                        .then(function (result) {
                            return self.env.pos.do_action(result);
                        });
//                }
            }

            async check_is_customer() {
                if (this.currentOrder.get_client()) {
                    return true;
                }
                const {confirmed} = await this.showPopup("ConfirmPopup", {
                    title: this.env._t("Please select the Customer"),
                    body: this.env._t("You need to select the customer."),
                });
                if (confirmed) {
                    this.selectClient();
                }
                return false;
            }

            async _isOrderValid(isForceValidate) {
                var order = this.currentOrder;
                var total_with_tax = order.get_total_with_tax();
                var valid = super._isOrderValid(isForceValidate);

                var paymentlines = order.get_paymentlines();
                if (!paymentlines.length) {
                    return false;
                }

                if (valid && total_with_tax < 0 && !order.get_client()) {
                    const {confirmed} = await this.showPopup("ConfirmPopup", {
                        title: this.env._t("Please select the Customer"),
                        body: this.env._t("You need to select the customer before you giving money to the customer."),
                    });
                    if (confirmed) {
                        this.selectClient();
                    }
                    return false;
                }
                return valid;
            }

            async validateOrder(isForceValidate) {
                var order = this.currentOrder;

                var res = super.validateOrder(isForceValidate);

                var change = order.get_change();
                var total_with_tax = order.get_total_with_tax();
                if (change > 0 && total_with_tax <= 0) {
                    // Se va fac un borderou de achzitie
                    order._tally_sheet = true;
                }
                return res;
            }

//            async _finalizeValidation() {
//                var order = this.currentOrder;
//
//                var negative = false;
//
//                var paymentlines = order.get_paymentlines();
//
//                paymentlines.forEach(function (paymentline) {
//                    if (!paymentline.is_change) {
//                        if (paymentline.amount < 0) {
//                            negative = true;
//                        }
//                    }
//                });
//                const ecr_file = new ECRFile();
//                if (negative) {
//                    ecr_file.prepare_dp(order);
//                } else {
//                    ecr_file.prepare_bf(order);
//                }
//                super._finalizeValidation();
//            }

            download(filename, textfile) {
                var blob = new Blob([textfile], {type: "application/octet-stream"});
                var element = document.createElement("a");

                element.setAttribute("href", URL.createObjectURL(blob));
                element.setAttribute("download", filename);

                element.style.display = "none";
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
                return true;
            }

            async _printWeb(isForceValidate) {
                if (await this._isOrderValid(isForceValidate)) {
                    var order = this.currentOrder;
                    if (!order) {
                        this.orderManagementContext = useContext(contexts.orderManagement);
                        order = this.orderManagementContext.selectedOrder;
                    } else if (order._printed) {
                        return true;
                    }

                    if (order._tally_sheet) {
                        order._printed = true;
                        return true;
                    }

//                    if (!order.file) {
                    var negative = false;

                    var paymentlines = order.get_paymentlines();

                    paymentlines.forEach(function (paymentline) {
                        if (!paymentline.is_change) {
                            if (paymentline.amount < 0) {
                                negative = true;
                            }
                        }
                    });
                    const ecr_file = new ECRFile();
                    if (negative) {
                        ecr_file.prepare_dp(order);
                    } else {
                        ecr_file.prepare_bf(order);
                    }
//                    }

                    var filename = this.env.pos.config.file_prefix + order.uid + "." + this.env.pos.config.file_ext;

                    if (order.get_total_with_tax() > 0){
                        return this.download(filename, order.file);
                    }
                } else {
                    return 1;
                }
            }

            print_the_receipt() {
                this._printWeb();
            }
        };

    Registries.Component.extend(PaymentScreen, ECRPaymentScreen);
});
