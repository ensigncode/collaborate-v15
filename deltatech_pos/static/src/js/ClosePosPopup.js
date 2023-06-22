odoo.define("deltatech_pos.ClosePosPopup", function (require) {
    "use strict";

    const ClosePosPopup = require("point_of_sale.ClosePosPopup");
    const Registries = require("point_of_sale.Registries");
    var ECRFile = require("deltatech_pos.ecr_file");

    const ECRClosePosPopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            printX() {
                const ecr_file = new ECRFile();
                var ecr = this.env.pos.db.get_ecr_setting(this.env.pos.config.ecr_type);
                var file = ecr.print_xz.format({type: "X"});
                var filename = "print_x." + this.env.pos.config.file_ext;
                return ecr_file.download(filename, file);
            }
            printZ() {
                const ecr_file = new ECRFile();
                var ecr = this.env.pos.db.get_ecr_setting(this.env.pos.config.ecr_type);
                var file = ecr.print_xz.format({type: "Z"});
                var filename = "print_z." + this.env.pos.config.file_ext;
                return ecr_file.download(filename, file);
            }
        };

    Registries.Component.extend(ClosePosPopup, ECRClosePosPopup);
});
