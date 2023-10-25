odoo.define('website_data_layer_specific.website_sale', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var WebsiteSaleCart = require('website_sale.cart');
    var WebsiteSale = require('website_sale.website_sale');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events || {}, {
            'click .o_product_link': '_onViewProduct',
            'click a.shop_checkout_process': '_onCheckoutProcess'
        }),

        getSelectedVariantName: function ($container) {
            var values = [];
            var unchangedValues = $container
                .find('div.oe_unchanged_value_ids')
                .data('unchanged_value_ids') || [];

            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            _.each(this.$el.find('.js_product').find(variantsValuesSelectors.join(', ')), function (el) {
                values.push($(el).data('value_name'));
            });

            return values.concat(unchangedValues);
        },

        _onViewProduct: function(ev){
            var href_url = $(ev.currentTarget)[0].dataset['hrefPath'];
            var product_image = $(ev.currentTarget).parent().find('img');
            var product_span = $(ev.currentTarget).parent().find("span.justify-content-center");
            var product_price = $(ev.currentTarget).parent().find("div.product_price");
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ ecommerce: null });
            window.dataLayer.push({
              event: 'view_item',
              ecommerce: {
                items: [{
                  item_name: product_image.attr('alt'),
                  item_id: product_span.data('oe-id'),
                  price: $(product_price.find('span[itemprop="price"]')[0]).html(),
                  item_brand: false,
                  item_category: false,
                  item_category2: false,
                  item_variant: false,
                  quantity: 2,
                }]
              }
            });
            window.location = href_url;
        },

        _submitForm: function () {
            const params = this.rootProduct;

            const $product = $('#product_detail');
            const productTrackingInfo = $product.data('product-tracking-info');
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ ecommerce: null });
            window.dataLayer.push({
              event: 'add_to_cart',
              ecommerce: {
                items: [{
                  item_name: productTrackingInfo['item_name'],
                  item_id: productTrackingInfo['item_id'],
                  price: productTrackingInfo['price'],
                  item_brand: productTrackingInfo['item_brand'] || false,
                  item_category: productTrackingInfo['item_category'],
                  item_category2: false,
                  item_variant: this.getSelectedVariantName(this.$el.find('.js_product')),
                  item_list_name: 'Search results',
                  item_list_id: 'search_results',
                  index: 1,
                  quantity:params.quantity,
                }]
              }
            });
            return this._super.apply(this, arguments);
        },

        onClickAddCartJSON: function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var closest_tr = $(ev.currentTarget).closest('tr');
            var $input = $link.closest('.input-group').find("input");
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
            if (newQty < previousQty || newQty == 0) {
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push({
                  event: 'remove_from_cart',
                  ecommerce: {
                    items: [{
                      item_name: closest_tr.find('td.td-product_name a').text().replace(/\n/g, '').replace(/\s+/g, ' ').trim(),
                      item_id: closest_tr.find('td.td-qty input').data('product-id'),
                      price: closest_tr.find('td.td-price span.oe_currency_value').text(),
                      item_brand: false,
                      item_category: false,
                      item_category2: false,
                      item_variant: false,
                      quantity: newQty,
                    }]
                  }
                });
            }
            return this._super.apply(this, arguments);
        },

        _onCheckoutProcess: function(ev) {
            var js_cart_lines = $(".js_cart_lines").first().find('tr').slice(1);;
            var productData = [];

			// Iterate through each <tr> element
			js_cart_lines.each(function() {
			    var $row = $(this);

			    // Extract the product name from the <strong> element
			    var productName = $row.find('.td-product_name strong').text();
			    var line_input = $row.find('.td-qty input');

			    // Extract the price from the .oe_currency_value element
			    var price = $row.find('.oe_currency_value').text();

			    productData.push({
					item_name: productName,
					item_id: line_input.data('product_id'),
					price: price,
					item_brand: false,
					item_category: false,
					item_category2: false,
					item_variant: false,
					quantity: line_input.val(),
			    });
			});

            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ ecommerce: null });
            window.dataLayer.push({
              event: 'begin_checkout',
              ecommerce: {
                items: productData
              }
            });
            window.location = '/shop/checkout?express=1';
        },
    })
})