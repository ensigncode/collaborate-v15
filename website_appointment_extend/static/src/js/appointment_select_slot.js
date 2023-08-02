odoo.define('website_appointment_extend.appointment_select_slot', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var select_appointment_slot = require('appointment.select_appointment_slot');
var core = require('web.core');

var _t = core._t;

/**
 * On click day slot check if slots are not available raise a warning
 */
publicWidget.registry.appointmentSlotSelect.include({
    _onClickDaySlot: function (ev) {
        var available_slots = $(ev.currentTarget).find('.o_slot_button').data('available-slots')
        if (available_slots != undefined && available_slots.length > 0){
            this._super(...arguments);
        } else {
            var message = _t("Locurile disponibile s-au epuizat. Verificati disponibilitatea in zilele urmatoare!")
            this.displayNotification({ message, sticky: false, type: 'danger' });
        }
    },
});

});
