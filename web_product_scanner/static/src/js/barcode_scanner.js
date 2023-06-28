odoo.define('web_product_scanner.barcode_scanner', function(require) {
	"use strict";

	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var Session = require('web.session');

	publicWidget.registry.appointmentForm = publicWidget.Widget.extend({
	    selector: '.o_product_scan_barcode_main_menu_container',

	    start: function() {
	        core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
	        return this._super().then(() => {
	            if (this.message_demo_barcodes) {
	                this.setup_message_demo_barcodes();
	            }
	        });
        },

        _onBarcodeScanned: function (barcode) {
	        if (!$.contains(document, this.el)) {
	            return;
	        }
	        Session.rpc('/fetch_product/'.concat(barcode)).then(result => {
	            if (typeof(result) == 'string'){
					this.displayNotification({ message: result, type: 'danger' });
	            } else{
	                var productInfo = $('#productInfoModal').find('.modal-body');
	                productInfo.find('.product-image').attr('src', result.product_image);
	                productInfo.find('.product-title').text(result.product_name);
	                productInfo.find('.product-price').text(result.product_price);
	                productInfo.find('.product-barcode').text(result.product_barcode);
	                $('#productInfoModal').modal('show');
	            }
	        });
	    },
	});

});