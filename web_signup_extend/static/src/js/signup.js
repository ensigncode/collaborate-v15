odoo.define("web_signup_extend.signup", function (require) {
    "use strict";

    var SignUpForm = require("auth_signup.signup");
    var publicWidget = require('web.public.widget');

    var SignUpFormWidget = publicWidget.registry.SignUpForm;

    SignUpFormWidget.include({

        events: Object.assign({}, SignUpFormWidget.prototype.events, {
            'change #agreed_on_tmc': 'onChangeTMC',
        }),

        init: function(){
            this._super.apply(this, arguments);
            $('button[type="submit"]').attr('disabled', 'disabled');
        },

        onChangeTMC: function(ev){
            // Enable, Disable submit button
            if ($('input[id="agreed_on_tmc"]')[0].checked){
                $('button[type="submit"]')[0].removeAttribute('disabled');
            } else {
                $('button[type="submit"]').attr('disabled', 'disabled');
            }

        }
    })

});