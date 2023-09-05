odoo.define('website_appointment_extend.appointment_select_slot', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var select_appointment_slot = require('appointment.select_appointment_slot');
var core = require('web.core');
var qweb = core.qweb;
var _t = core._t;

/**
 * On click day slot check if slots are not available raise a warning
 */
publicWidget.registry.appointmentSlotSelect.include({

    xmlDependencies: ['/appointment/static/src/xml/calendar_appointment_slots.xml', '/website_appointment_extend/static/src/xml/appointment_slot.xml'],

    _onClickDaySlot: function (ev) {
        this.$('.o_slot_selected').removeClass('o_slot_selected');
        this.$(ev.currentTarget).addClass('o_slot_selected');
        const appointmentTypeID = this.$("input[name='appointment_type_id']").val();
        const appointmentTypeIDs = this.$("input[name='filter_appointment_type_ids']").val();
        const slotDate = this.$(ev.currentTarget.firstElementChild).attr('id');
        const slots = this.$(ev.currentTarget).find('div')[0].dataset['availableSlots'] != undefined ? JSON.parse(this.$(ev.currentTarget).find('div')[0].dataset['availableSlots']) : [];

        let $slotsList = this.$('#slotsList').empty();
        $(qweb.render('appointment.slots_list', {
            slotDate: moment(slotDate).format("dddd D MMMM"),
            slots: slots,
            appointment_type_id: appointmentTypeID,
            filter_appointment_type_ids: appointmentTypeIDs,
        })).appendTo($slotsList);
    },
});

});
