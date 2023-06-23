odoo.define('web_signup_extend.portal', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const {_t, qweb} = require('web.core');
    const ajax = require('web.ajax');
    const session = require('web.session');

    publicWidget.registry.portalDetailsAccount = publicWidget.Widget.extend({
        selector: '.o_portal_my_security',
//        events: {
//            'click a#delete_my_account': '_onDeleteAccount',
//        },
//
//       _onDeleteAccount: function(ev){
//			ev.preventDefault();
//			$('#confirmModal').modal({
//				backdrop: 'static',
//				keyboard: false
//			})
//			.on('click', '#confirmOk', function(e) {
////				$.ajax({
////					url: "/my/account/delete",
////					data: {},
////					type: 'POST',
////					processData: false,
////					contentType: false,
////					success: function(result) {
////						return result
////					}
////
////				});
//				return ajax.rpc('/my/account/delete', {}).then((result) => {
//					console.log("result", result);
//					return result
//				});
//			});
//       },
    });
});
