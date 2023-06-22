odoo.define("deltatech_pos.CashOpeningPopup", function (require) {
    "use strict";

    const CashOpeningPopup = require("point_of_sale.CashOpeningPopup");
    const Registries = require("point_of_sale.Registries");
    var ECRFile = require("deltatech_pos.ecr_file");

    const ECRCashBoxOpening = (CashOpeningPopup) =>
        class extends CashOpeningPopup {
            startSession() {
                super.startSession();
                const cashOpening = this.env.pos.bank_statement.balance_start;
                if (cashOpening > 0) {
                    const ecr_file = new ECRFile();
                    var ecr = this.env.pos.db.get_ecr_setting(this.env.pos.config.ecr_type);
                    var file = ecr.in.format({value: ecr.amount(cashOpening)});
                    var filename = "cash_open." + this.env.pos.config.file_ext;
                    return ecr_file.download(filename, file);
                }
            }
        };

    Registries.Component.extend(CashOpeningPopup, ECRCashBoxOpening);
});
