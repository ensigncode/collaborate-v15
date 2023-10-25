odoo.define('website_data_layer_specific.website_sale_validate', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var WebsiteSaleCart = require('website_sale.cart');
    var WebsiteSale = require('website_sale.website_sale');
    var WebsiteSaleValidate = require('website_sale.validate');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.websiteSaleValidate.include({
		_paymentTransationPollStatus: function () {
			var self = this;
			this._super.apply(this, arguments).then(function(ev){
				self._rpc({
		            route: '/shop/payment/track_payment/' + parseInt(self.$el.data('order-id')),
		        }).then(function (result) {
                    window.dataLayer = window.dataLayer || [];
					window.dataLayer.push({ ecommerce: null });
					window.dataLayer.push({
						event: 'purchase',
						ecommerce: result
					});
		        })
			});

		}
    })
})
