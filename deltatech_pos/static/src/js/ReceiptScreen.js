odoo.define("deltatech_pos.ReceiptScreen", function (require) {
    "use strict";

    const AbstractReceiptScreen = require("point_of_sale.AbstractReceiptScreen");
    const {useContext} = owl.hooks;
    const contexts = require("point_of_sale.PosContext");

    const Registries = require("point_of_sale.Registries");
    var ECRFile = require("deltatech_pos.ecr_file");
    // Var models = require("point_of_sale.models");

    /*    If (!String.prototype.format) {
        String.prototype.format = function () {
            var args = arguments;
            if (args.length === 1 && args[0] !== null && typeof args[0] === "object") {
                args = args[0];
            }
            return this.replace(/{([^}]*)}/g, function (match, key) {
                return typeof args[key] !== "undefined" ? args[key] : match;
            });
        };
    }*/

    /*
    function replaceDiacritics(str) {
        var diacritics = [
            {char: "A", base: /[\u0102\u00C2]/g},
            {char: "a", base: /[\u0103\u00E2]/g},
            {char: "I", base: /[\u00CE]/g},
            {char: "i", base: /[\u00EE]/g},
            {char: "S", base: /[\u0218\u015E]/g},
            {char: "s", base: /[\u0219\u015F]/g},
            {char: "T", base: /[\u021A\u0162]/g},
            {char: "t", base: /[\u021B\u0163]/g},
        ];

        diacritics.forEach(function (letter) {
            str = str.replace(letter.base, letter.char);
        });

        return str;
    }
*/

    const ECRReceiptScreen = (AbstractReceiptScreen) =>
        class extends AbstractReceiptScreen {
            constructor() {
                super(...arguments);
                this.orderManagementContext = useContext(contexts.orderManagement);
            }
            /*
            Prepare_line_bf(ecr, orderline) {
                var prod_name = "";
                var prodname = "";
                var price = 0;
                var taxes = "";
                var line = "";
                var text_line = "";

                var product_display_name = orderline.product.display_name;
                product_display_name = product_display_name.replace(/,/g, " ");
                product_display_name = product_display_name.replace(/;/g, " ");

                // Verifying length...
                if (product_display_name.length <= ecr.limit) {
                    prod_name = product_display_name;
                } else {
                    prod_name = product_display_name.substring(0, ecr.limit);
                    prodname = product_display_name;
                }
                taxes = orderline.get_taxes();
                //            Var mapped_included_taxes = [];
                var taxes_ids = [];
                _(taxes).each(function (tax) {
                    var line_taxs = orderline._map_tax_fiscal_position(tax);
                    _(line_taxs).each(function (line_tax) {
                        if (tax.id !== line_tax.id) {
                            taxes_ids.push(line_tax);
                        }
                    });
                });
                if (taxes_ids.length !== taxes.length) {
                    taxes_ids = taxes;
                }
                // Var taxes_ids = orderline.product.taxes_id;

                taxes = orderline.pos.taxes;
                // Var taxdetail = {};
                // var product_taxes = [];
                var tax = 1;
                if (taxes_ids === "") {
                    // Without taxes
                    tax = ecr.cod_tva.without;
                }
                //            _(taxes_ids).each(function(el){
                //                var oTax = _.detect(taxes, function(t){
                //                    return t.id === el;
                //                });
                //                tax =  ecr.cod_tva[oTax.amount];
                //
                //                product_taxes.push(oTax);
                //            });
                // pretul trebuie sa fie cu tot cu tva?
                _(taxes_ids).each(function (el) {
                    tax = ecr.cod_tva[el.amount];
                });
                price = orderline.get_price_with_tax_before_discount() / ecr.qty(orderline.quantity);
                // Price = orderline.price
                if ((price > 0 && orderline.quantity > 0) || ecr.ok_negative) {
                    line = ecr.sale.format({
                        name: prod_name,
                        price: ecr.amount(price),
                        qty: ecr.qty(orderline.quantity),
                        dep: ecr.department(tax),
                        group: "1",
                        storno: "0",
                        percent: "",
                        netto: "",
                        // De adus codul de taxa model
                        tax: tax,
                        uom: orderline.product.uom_id[1],
                    });
                } else {
                    // Printing global discount
                    // printing subtotal
                    line = ecr.subtotal;
                    // Printing discount
                    price = orderline.get_price_with_tax_before_discount();
                    line = line + "\r\n" + ecr.discount.format({type: 3, value: price});
                }
                text_line = text_line + line + "\r\n";

                if (product_display_name.length > ecr.limit) {
                    var regexp = new RegExp(".{1," + ecr.limit + "}", "g");
                    var d_array = prodname.match(regexp);
                    for (var j = 1; j < d_array.length; j++) {
                        line = ecr.print.format({text: d_array[j]});
                        text_line = text_line + line + "\r\n";
                    }
                }
                if (orderline.discount > 0) {
                    line = ecr.discount.format({type: 1, value: ecr.amount(orderline.discount)});
                    text_line = text_line + line + "\r\n";
                }

                return text_line;
            }

            prepare_header(ecr, order) {
                var textfile = "";
                var line = "";
                var client = order.get_client();
                if (client) {
                    line = ecr.print.format({text: this.env._t("Customer:") + client.name});
                    textfile = textfile + line + "\r\n";
                    if (client.vat) {
                        line = ecr.print.format({text: "CUI:" + client.vat});
                        textfile = textfile + line + "\r\n";
                    }
                }

                var reference = order.uid;
                line = ecr.print.format({text: reference});
                textfile = textfile + line + "\r\n";
                if (order.note) {
                    line = ecr.print.format({text: order.note});
                    textfile = textfile + line + "\r\n";
                }
                return textfile;
            }

            prepare_bf(order) {
                var textfile = "";
                var line = "";

                var cod_ecr = "";

                var i = 0;
                var paymentline = "";
                var ecr = this.env.pos.db.get_ecr_setting(this.env.pos.config.ecr_type);

                textfile = this.prepare_header(ecr, order);

                // Textfile = textfile + ecr.p +reference+'\r\n';
                var orderlines = order.get_orderlines();
                for (i = 0; i < orderlines.length; i++) {
                    var orderline = orderlines[i];
                    var textline = this.prepare_line_bf(ecr, orderline);
                    textfile += textline;
                }
                var paymentlines = order.get_paymentlines();
                // Plata prin banca
                for (i = 0; i < paymentlines.length; i++) {
                    paymentline = paymentlines[i];

                    cod_ecr = paymentline.payment_method.cod_ecr;
                    if (!paymentline.payment_method.is_cash_count) {
                        line = ecr.total.format({type: cod_ecr, amount: ecr.amount(paymentline.amount)});
                        textfile = textfile + line + "\r\n";
                    }
                }
                // Numerar
                // var change = order.get_change();
                // var amount = 0;
                for (i = 0; i < paymentlines.length; i++) {
                    paymentline = paymentlines[i];

                    cod_ecr = paymentline.payment_method.cod_ecr;
                    if (paymentline.payment_method.is_cash_count && !paymentline.is_change) {
                        // Amount = paymentline.amount;
                        // Sper ca  stie casa sa calculeze restul
                        // if (change < amount) {
                        //     amount -= change;
                        //     change = 0;
                        // }
                        line = ecr.total.format({type: cod_ecr, amount: ecr.amount(paymentline.amount)});
                        textfile = textfile + line + "\r\n";
                    }
                }

                order.file = replaceDiacritics(textfile);
                // Order.file = new Blob([replaceDiacritics(textfile)], {type: "application/octet-stream"});
            }

            prepare_dp(order) {
                // Pregatire dispozitie de plata
                var self = this;

                var textfile = "";
                var line = "";

                var prod_name = "";
                var price = "";

                var ecr = this.env.pos.db.get_ecr_setting(this.env.pos.config.ecr_type);

                textfile = this.prepare_header(ecr, order);

                var orderlines = order.get_orderlines();

                orderlines.forEach(function (orderline) {
                    var product_display_name = orderline.product.display_name;
                    product_display_name = product_display_name.replace(/,/g, " ");
                    product_display_name = product_display_name.replace(/;/g, " ");
                    if (product_display_name.length <= ecr.limit) {
                        prod_name = product_display_name;
                    } else {
                        prod_name = product_display_name.substring(0, ecr.limit);
                    }
                    line = ecr.print.format({text: prod_name});

                    line = ecr.print.format({text: self.env._t("Cant:") + orderline.quantity});
                    price = orderline.get_price_with_tax() / ecr.qty(orderline.quantity);
                    line = ecr.print.format({text: self.env._t("Price:") + price});
                });

                var paymentlines = this.currentOrder.get_paymentlines();
                paymentlines.forEach(function (paymentline) {
                    if (paymentline.amount < 0) {
                        line = ecr.out.format({value: ecr.amount(-paymentline.amount)});
                    } else {
                        line = ecr.in.format({value: ecr.amount(paymentline.amount)});
                    }
                    textfile = textfile + line + "\r\n";
                });

                order.file = replaceDiacritics(textfile);
                // Order.file = new Blob([replaceDiacritics(textfile)], {type: "application/octet-stream"});
            }

        */
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

            async _printWeb() {
                var order = this.currentOrder;
                if (!order) {
                    order = this.orderManagementContext.selectedOrder;
                } else if (order._printed) {
                    return true;
                }

                if (order._tally_sheet) {
                    order._printed = true;
                    return true;
                }

                if (!order.file) {
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
                }

                var filename = this.env.pos.config.file_prefix + order.uid + "." + this.env.pos.config.file_ext;

                return this.download(filename, order.file);
            }
        };

    Registries.Component.extend(AbstractReceiptScreen, ECRReceiptScreen);
});
