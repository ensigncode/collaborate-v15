odoo.define('pos_split_refund_discount.models', function (require) {
"use strict";

    const models = require('point_of_sale.models');

    var _order_super = models.Order.prototype;
    var _orderline_super = models.Orderline.prototype;

    models.Order = models.Order.extend({
        init_from_JSON: function(json) {
            _order_super.init_from_JSON.apply(this, arguments);
            if (json.applied_program_ids) {
                this.applied_program_ids = json.applied_program_ids;
            }
        }
    });

    models.Orderline = models.Orderline.extend({
        init_from_JSON: function(json) {
            _orderline_super.init_from_JSON.apply(this, arguments);
            if (json.is_program_reward) {
                this.is_program_reward = json.is_program_reward;
            }
            if (json.program_id) {
                this.program_id = json.program_id;
            }
        }
    });
});