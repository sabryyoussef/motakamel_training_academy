odoo.define('motakamel_workflow_dashboard.WorkflowNavigation', function (require) {
    'use strict';

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var _t = core._t;

    var WorkflowNavigation = AbstractAction.extend({
        template: 'motakamel_workflow_dashboard.WorkflowNavigation',

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.workflowId = action.context.workflow_id;
        },

        start: function () {
            this._super.apply(this, arguments);
            this._setupNavigation();
        },

        _setupNavigation: function () {
            var self = this;
            
            // Setup breadcrumb navigation
            this._setupBreadcrumbs();
            
            // Setup quick actions
            this._setupQuickActions();
            
            // Setup progress tracking
            this._setupProgressTracking();
        },

        _setupBreadcrumbs: function () {
            // Add breadcrumb navigation
            var breadcrumbs = [
                { name: _t('Workflow Dashboard'), url: '#' },
                { name: _t('Current Workflow'), url: '#' }
            ];
            
            // Render breadcrumbs
            this.$('.o_breadcrumb').html(this._renderBreadcrumbs(breadcrumbs));
        },

        _setupQuickActions: function () {
            var self = this;
            
            // Quick action buttons
            var quickActions = [
                { name: _t('View Stages'), icon: 'fa-list', action: 'view_stages' },
                { name: _t('View Analytics'), icon: 'fa-chart-bar', action: 'view_analytics' },
                { name: _t('Setup Workflow'), icon: 'fa-cogs', action: 'setup_workflow' }
            ];
            
            // Render quick actions
            this.$('.o_quick_actions').html(this._renderQuickActions(quickActions));
        },

        _setupProgressTracking: function () {
            var self = this;
            
            // Progress tracking setup
            this.$('.o_progress_tracking').html(this._renderProgressTracking());
        },

        _renderBreadcrumbs: function (breadcrumbs) {
            var html = '<nav aria-label="breadcrumb"><ol class="breadcrumb">';
            breadcrumbs.forEach(function (crumb, index) {
                var activeClass = index === breadcrumbs.length - 1 ? ' active' : '';
                html += '<li class="breadcrumb-item' + activeClass + '">' + crumb.name + '</li>';
            });
            html += '</ol></nav>';
            return html;
        },

        _renderQuickActions: function (actions) {
            var html = '<div class="btn-group" role="group">';
            actions.forEach(function (action) {
                html += '<button type="button" class="btn btn-outline-primary" data-action="' + action.action + '">';
                html += '<i class="fa ' + action.icon + '"></i> ' + action.name;
                html += '</button>';
            });
            html += '</div>';
            return html;
        },

        _renderProgressTracking: function () {
            return '<div class="progress"><div class="progress-bar" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100">25% Complete</div></div>';
        },

        // Event handlers
        _onQuickActionClick: function (event) {
            var action = $(event.currentTarget).data('action');
            this._handleQuickAction(action);
        },

        _handleQuickAction: function (action) {
            switch (action) {
                case 'view_stages':
                    this._viewStages();
                    break;
                case 'view_analytics':
                    this._viewAnalytics();
                    break;
                case 'setup_workflow':
                    this._setupWorkflow();
                    break;
            }
        },

        _viewStages: function () {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Workflow Stages'),
                res_model: 'motakamel.workflow.stage',
                view_mode: 'tree,form',
                domain: [('workflow_id', '=', this.workflowId)],
                target: 'current'
            });
        },

        _viewAnalytics: function () {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Workflow Analytics'),
                res_model: 'motakamel.workflow.analytics',
                view_mode: 'tree,form',
                domain: [('workflow_id', '=', this.workflowId)],
                target: 'current'
            });
        },

        _setupWorkflow: function () {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Workflow Setup'),
                res_model: 'motakamel.workflow.setup.wizard',
                view_mode: 'form',
                target: 'new',
                context: { default_workflow_id: this.workflowId }
            });
        }
    });

    core.action_registry.add('motakamel_workflow_navigation', WorkflowNavigation);

    return WorkflowNavigation;
});
