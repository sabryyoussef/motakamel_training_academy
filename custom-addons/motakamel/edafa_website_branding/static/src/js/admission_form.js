/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

// Global function to clear demo data
window.clearDemoData = function() {
    if (confirm('Are you sure you want to clear all demo data?')) {
        document.getElementById('admissionForm').reset();
    }
};

odoo.define('edafa_website_branding.admission_form', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.AdmissionForm = publicWidget.Widget.extend({
        selector: '.admission-form',
        events: {
            'change select[name="country_id"]': '_onCountryChange',
            'submit': '_onFormSubmit',
        },

        /**
         * Initialize the form
         */
        start: function () {
            this._super.apply(this, arguments);
            // Add form validation
            this._setupValidation();
        },

        /**
         * Handle country selection change to update states
         */
        _onCountryChange: function (ev) {
            var self = this;
            var countryId = $(ev.currentTarget).val();
            var $stateSelect = this.$el.find('select[name="state_id"]');

            if (!countryId) {
                $stateSelect.html('<option value="">Select State...</option>');
                return;
            }

            // Fetch states for selected country
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model: 'res.country.state',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['country_id', '=', parseInt(countryId)]],
                    fields: ['id', 'name'],
                    context: {},
                }
            }).then(function (states) {
                var options = '<option value="">Select State...</option>';
                states.forEach(function (state) {
                    options += '<option value="' + state.id + '">' + state.name + '</option>';
                });
                $stateSelect.html(options);
            });
        },

        /**
         * Setup form validation (DISABLED FOR TESTING)
         */
        _setupValidation: function () {
            // Validation disabled for testing
            return;
        },

        /**
         * Handle form submission
         */
        _onFormSubmit: function (ev) {
            // Validation disabled for testing - just add loading state
            this.$el.addClass('loading');
            this.$el.find('button[type="submit"]').prop('disabled', true);
            this.$el.find('button[type="submit"]').html('<i class="fa fa-spinner fa-spin"></i> Submitting...');
        },
    });

    return publicWidget.registry.AdmissionForm;
});

