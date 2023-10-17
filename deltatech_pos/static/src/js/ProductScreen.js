odoo.define("deltatech_pos.ProductScreen", function (require) {
    "use strict";

    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");
    const {useListener} = require("web.custom_hooks");

    const ECRProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                useListener("click-pay", this._onClickPay);
            }
            _onClickPay() {
                var self = this;
                var order = this.currentOrder;
                var orderlines = order.get_orderlines();
                var ok = true;
                var tva = {};
                var key = "";
                orderlines.forEach(function (orderline) {
                    if (tva[orderline.product.taxes_id]) {
                        tva[orderline.product.taxes_id] += orderline.price * orderline.quantity;
                    } else {
                        tva[orderline.product.taxes_id] = orderline.price * orderline.quantity;
                    }
                    if (!orderline.quantity && ok) {
                        ok = false;
                        self.showPopup("ErrorPopup", {
                            title: self.env._t("Invalid action"),
                            body: self.env._t("It is not allowed to have products without quantity"),
                        });
                    }
                });
                var count = 0;
                for (key in tva) {
                    count++;
                }
                if (count > 1) {
                    for (key in tva) {
                        if (tva[key] < 0) {
                            ok = false;
                            self.showPopup("ErrorPopup", {
                                title: self.env._t("Invalid action"),
                                body: self.env._t(
                                    "The value of the refunded products must be less than the value of the products purchased on each VAT rate"
                                ),
                            });
                        }
                    }
                }
                if (ok) {
                    super._onClickPay();
                }
            }
        };

    Registries.Component.extend(ProductScreen, ECRProductScreen);
});
