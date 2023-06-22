odoo.define("deltatech_pos.DB", function (require) {
    "use strict";

    var PosDB = require("point_of_sale.DB");
    var models = require("point_of_sale.models");

    models.load_fields("pos.payment.method", ["cod_ecr"]);
    models.load_fields("pos.order", ["file"]);

    var _super = models.Order;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.file = this.file;
            return json;
        },

        remove_paymentline: function () {
            _super.prototype.remove_paymentline.apply(this, arguments);
            if (this.get_total_paid() === 0) {
                this.amount_return = 0;
            }
        },
    });

    PosDB.include({
        _partner_search_string: function (partner) {
            var str = this._super(partner);
            str = str.replace("\n", "");
            if (partner.vat) {
                str += "|" + partner.vat;
            }
            return str + "\n";
        },

        get_ecr_setting: function (ecr_type) {
            var ecr = {};
            switch (ecr_type) {
                case "datecs18":
                    ecr = {
                        // Comanda print
                        print: "P,1,______,_,__;{text};;;;",
                        reference: "P,1,______,_,__;{text};;;;",
                        // Comanda sale
                        sale: "S,1,______,_,__;{name};{price};{qty};{dep};{group};{tax};0;0;{uom};",
                        // Comanda de inchidere
                        total: "T,1,______,_,__;{type};{amount};;;;",

                        cif: "K,1,______,_,__;{cif};",
                        discount: "C,1,______,_,__;{type};{value};;;;",
                        subtotal: "L,1,______,_,__;",
                        in: "I,1,______,_,__;0;{value};;;;",
                        out: "I,1,______,_,__;1;{value};;;;",
                        limit: 72,
                        ok_negative: true,
                        require_subtotal: false,
                        department: function () {
                            return "1";
                        },
                        amount: function (value) {
                            return value.toFixed(2);
                        },
                        qty: function (value) {
                            return value.toFixed(3);
                        },
                        cod_tva: {without: "6", 19: "19%", 9: "9%", 5: "5%"},
                        barcode128: "Q,1,______,_,__;3;{value}",
                        print_xz: "{type},1,______,_,__;;;;;;;",
                    };
                    break;
                case "incotex":
                    ecr = {
                        // Comanda print
                        print: 'R_TXT "{text}"',
                        reference: 'R_VRN "{text}"',
                        // Comanda sale
                        sale: 'R_TRP "{name}" {qty}{uom} * {price} V{tax}',
                        // Comanda de inchidere
                        total: "R_PM{type} {amount}",
                        cif: 'R_TIN "{cif}"',
                        discount: "R_DMP +{value}",
                        subtotal: "R_STT pd",
                        in: 'R_TXT "in {value}"',
                        out: 'R_TXT "out {value}"',
                        limit: 28,
                        ok_negative: true,
                        require_subtotal: true,
                        department: function () {
                            return "D1";
                        },
                        amount: function (value) {
                            return value.toFixed(2);
                        },
                        qty: function (value) {
                            return value.toFixed(3);
                        },
                        cod_tva: {without: "1", 19: "2", 9: "3", 18: "2", 0: "3"},
                        barcode128: "",
                        print_xz: "C_DY{type}",
                    };
                    break;
                case "fiscalnet":
                    ecr = {
                        // Comanda print
                        print: "TL^{text}",
                        reference: "TL^{text}",
                        // Comanda sale
                        /*
                        S^DENUMIRE ARTICOL^PRET^CANTITATE^UM^GRTVA^GRDEP
                        PRET – cu 2 zecimale fara delimitator (ex. 1000 – pentru 10 RON)
                        CANTITATE – cu 3 zecimale fara delimitator (ex. 1000 – pentru 1)
                        GRTVA – grupa de TVA (1,2,3,4,5)
                        GRDEP – grupa de articole, daca modelul de casa suporta (1,2,3,4,5,…) daca nu se
                        completeaza cu 1

                         */

                        sale: "S^{name}^{price}^{qty}^{uom}^{tax}^{dep}",
                        // Comanda de inchidere
                        /*
                        P^TipPlata(1,2,3,4,5,…)^VALOARE
                        Tipuri de plata: 1=Numerar, 2=Card, 3=Credit, 4=Tichet masa, 5=Tichet valoric, 6=Voucher, 7=Plata moderna,
                        8=Alte modalitati, 9=Alte modalitati
                         */
                        total: "P^{type}^{amount}",
                        cif: "CF^{cif}",
                        discount: "DV^{value}",
                        subtotal: "ST^",
                        in: "I^{value}",
                        out: "O^{value}",
                        limit: 72,
                        ok_negative: false,
                        require_subtotal: false,
                        department: function () {
                            return "1";
                        },

                        amount: function (value) {
                            return value.toFixed(2);
                        },
                        qty: function (value) {
                            return value.toFixed(3);
                        },
                        cod_tva: {without: "6", 19: "1", 9: "2", 5: "3"},
                        barcode128: "",
                        print_xz: "{type}^",
                    };
                    break;
                case "succes":
                    ecr = {
                        // Comanda print
                        print: 'R_TXT "{text}"',
                        reference: 'R_TXT "{text}"',
                        // R_TRP “Text1””Text2”[QTTY[MSRUNIT]*][AMOUNT VAT] | [ [AMOUNT] DEPT]
                        // Comanda sale
                        sale: 'R_TRP "{name}"""{qty}{uom}*{price}V{tax}',
                        // Comanda de inchidere
                        total: "R_PM{type} {amount}",
                        cif: 'T_TIN "{cif}"',
                        discount: "R_DMP +{value}",
                        subtotal: "R_STT P",
                        in: 'R_TXT "{value}"',
                        out: 'R_TXT "{value}"',
                        limit: 28,
                        ok_negative: false,
                        require_subtotal: false,
                        department: function () {
                            return "1";
                        },
                        amount: function (value) {
                            return value.toFixed(2);
                        },
                        qty: function (value) {
                            return value.toFixed(3);
                        },
                        cod_tva: {without: 1, 19: 3, 9: 4, 5: 5},
                        barcode128: "",
                        print_xz: "C_DY{type}",
                    };
                    break;

                case "daisy":
                    ecr = {
                        // Comanda print
                        print: "P,1,______,_,__;{text};;;;;",
                        reference: "P,1,______,_,__;{text};;;;;",
                        // Sale:'S,1,______,_,__;{name};{price};{qty};{dep};{group};{tax};0;0;{uom};', // comanda sale
                        // R – sale by PLU.
                        // R,[logical number],_____,_,__;[PLU];[quantity];[storno];[percent];[price];[netto];

                        // E – sale by department
                        //    Е,1,______,_,__;;[price];[quantity];;;[department];[storno];[percent];[netto];
                        // Comanda sale
                        sale: "E,1,______,_,__;;{price};{qty};;;{dep};{storno};{percent};{netto};",
                        // Q – programming a department.
                        // Q,[logical number],_____,_,__;[No];[name];[TAX group];[price];[maxdigit];[measure];
                        // Comanda de inchidere
                        total: "T,1,______,_,__;{type};{amount};;;;",
                        // Comanda de tiparire CIF
                        cif: "T,1,______,_,__;;;{cif};;;",
                        discount: "C,1,______,_,__;{type};{value};;;;",
                        in: "P,1,______,_,__;{value};;;;;",
                        out: "P,1,______,_,__;{value};;;;;",
                        limit: 30,
                        ok_negative: false,
                        require_subtotal: false,
                        department: function (value) {
                            return "9" + value;
                        },
                        amount: function (value) {
                            return value.toFixed(2);
                        },
                        qty: function (value) {
                            return value.toFixed(3);
                        },
                        cod_tva: {without: 6, 19: 1, 9: 2, 5: 3},
                        barcode128: "Q,1,______,_,__;3;{value}",
                        print_xz: "{type},1,______,_,__;;;;;;;",
                    };
                    break;
                case "optima":
                    ecr = {
                        // Comanda print
                        print: "2;{text}",
                        reference: "2;{text}",
                        // Comanda sale
                        sale: "1;{name};1;1;{price};{qty}",
                        // Comanda de inchidere
                        total: "5;{amount};{type};1;0",
                        cif: "2;{cif}",
                        discount: "2;{value}",
                        in: "2;{value}",
                        out: "2;{value}",
                        limit: 18,
                        ok_negative: false,
                        require_subtotal: false,
                        department: function () {
                            return "1";
                        },
                        amount: function (value) {
                            return value * 100;
                        },
                        qty: function (value) {
                            return value * 100000;
                        },
                        cod_tva: {without: 6, 19: 1, 9: 2, 5: 3},
                        barcode128: "",
                        print_xz: "2;{type}",
                    };
                    break;
            }
            return ecr;
        },
    });
});
