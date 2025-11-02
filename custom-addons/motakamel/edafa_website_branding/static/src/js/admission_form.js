/** @odoo-module **/

// Pure ESM module to avoid legacy dependency resolution problems on website
import { jsonrpc } from "@web/core/network/rpc_service";
import publicWidget from "@web/legacy/js/public/public_widget";

// Global function to clear demo data (empties fields rather than resetting to defaults)
window.clearDemoData = function () {
    if (!confirm('Are you sure you want to clear all demo data?')) {
        return;
    }
    const form = document.getElementById('admissionForm');
    if (!form) return;

    const elements = form.querySelectorAll('input, select, textarea');
    elements.forEach((el) => {
        // keep csrf token
        if (el.name === 'csrf_token') return;

        if (el.tagName === 'SELECT') {
            el.selectedIndex = 0;
            return;
        }
        switch (el.type) {
            case 'checkbox':
            case 'radio':
                el.checked = false;
                break;
            case 'file':
                el.value = '';
                break;
            default:
                el.value = '';
        }
    });

    // Clear state options back to placeholder if present
    const stateSelect = form.querySelector('select[name="state_id"]');
    if (stateSelect) {
        stateSelect.innerHTML = '<option value="">Select State...</option>';
    }
};

publicWidget.registry.AdmissionForm = publicWidget.Widget.extend({
    selector: '.admission-form',
    events: {
        'change select[name="country_id"]': '_onCountryChange',
        'submit': '_onFormSubmit',
    },

    // Initialize the form
    start: function () {
        this._super.apply(this, arguments);
        this._setupValidation();
    },

    // Handle country selection change to update states
    _onCountryChange: function (ev) {
        const countryId = ev.currentTarget.value;
        const $stateSelect = this.$el.find('select[name="state_id"]');

        if (!countryId) {
            $stateSelect.html('<option value="">Select State...</option>');
            return;
        }

        // Fetch states for selected country
        jsonrpc('/web/dataset/call_kw', {
            model: 'res.country.state',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: [['country_id', '=', parseInt(countryId)]],
                fields: ['id', 'name'],
                context: {},
            },
        }).then((states) => {
            let options = '<option value="">Select State...</option>';
            states.forEach((state) => {
                options += `<option value="${state.id}">${state.name}</option>`;
            });
            $stateSelect.html(options);
        });
    },

    // Setup form validation (DISABLED FOR TESTING)
    _setupValidation: function () {
        return; // intentionally disabled
    },

    // Handle form submission
    _onFormSubmit: function () {
        this.$el.addClass('loading');
        this.$el.find('button[type="submit"]').prop('disabled', true);
        this.$el.find('button[type="submit"]').html('<i class="fa fa-spinner fa-spin"></i> Submitting...');
    },
});

