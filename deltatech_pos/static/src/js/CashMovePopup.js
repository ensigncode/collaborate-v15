odoo.define("deltatech_pos.CashMovePopup", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const CashMovePopup = require("point_of_sale.CashMovePopup");
    var ECRFile = require("deltatech_pos.ecr_file");

    const ECRCashMovePopup = (CashMovePopup) =>
        class extends CashMovePopup {
            confirm() {
                super.confirm();
                if (!this.state.inputHasError) {
                    var res = this.getPayload();
                    const ecr_file = new ECRFile();
                    var ecr = this.env.pos.db.get_ecr_setting(this.env.pos.config.ecr_type);
                    var file = "";
                    if (res.type === "in") {
                        file = ecr.in.format({value: ecr.amount(res.amount)});
                    } else {
                        file = ecr.out.format({value: ecr.amount(res.amount)});
                    }

                    var filename = "cash_move." + this.env.pos.config.file_ext;
                    return ecr_file.download(filename, file);
                }
            }
        };

    Registries.Component.extend(CashMovePopup, ECRCashMovePopup);
});
