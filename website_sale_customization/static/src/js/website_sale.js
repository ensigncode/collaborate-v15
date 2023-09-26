odoo.define('website_add_to_cart.website_sale', function (require) {
    "use strict";
    var core = require('web.core');
    var wSaleUtils = require('website_sale.utils');
    var websiteSale = require('website_sale.website_sale');
    var publicWidget = require('web.public.widget');

    // Override or extend a function from the original module
    publicWidget.registry.WebsiteSale.include({

        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events || {}, {
            'click .cart_buttons .a-submit': 'async _onClickAdd',
        }),

        async _onClickAdd(ev) {
            ev.preventDefault();
            const targetSelector = ev.currentTarget.dataset.animationSelector || 'img';
            this.$itemImgContainer = this.$(ev.currentTarget).closest(`:has(${targetSelector})`);
            var def = () => {
                this.isBuyNow = $(ev.currentTarget).attr('id') === 'buy_now';
                return this._handleAdd($(ev.currentTarget).closest('form'));
            };
            if ($('.js_add_cart_variants').children().length) {
                return this._getCombinationInfo(ev).then(() => {
                    return !$(ev.target).closest('.js_product').hasClass("css_not_available") ? def() : Promise.resolve();
                });
            }
            var $navButton = $('header .o_wsale_my_cart').first();
            await wSaleUtils.animateClone($('header .o_wsale_my_cart').first(), this.$itemImgContainer, 25, 40);
            return def();
        },
    });
});
