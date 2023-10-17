odoo.define("sostenia_auto_invoicing_shipping.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    var _super = models.Order;
    models.Order = models.Order.extend({
        initialize: function (attributes,options) {
            _super.prototype.initialize.apply(this, arguments);
            this.to_invoice = true;
            this.to_ship = true;
        },

        init_from_JSON: function(json){
            _super.prototype.init_from_JSON.apply(this,arguments);
            this.to_invoice = true;
            this.to_ship = true;
        },
    });
});