/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class WorkflowNavigation extends Component {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        
        // Get workflow context from props
        const context = this.props.action?.context || {};
        this.workflowId = context.workflow_id;
        this.workflowName = context.workflow_name || "Workflow";
        
        // State for stages
        this.state = useState({
            stages: [],
            loading: true
        });
        
        // Load stages on component start
        onWillStart(async () => {
            await this.loadStages();
        });
    }
    
    async loadStages() {
        try {
            const stages = await this.orm.searchRead(
                'motakamel.workflow.stage',
                [['workflow_id', '=', this.workflowId]],
                ['name', 'description', 'color', 'sequence', 'action_xml_ids', 'module_xml_ids'],
                { order: 'sequence' }
            );
            
            console.log('Loaded stages:', stages);
            
            // TEMPORARILY DISABLED - Filter stages based on user access rights
            // const filteredStages = await this.filterStagesByAccess(stages);
            // this.state.stages = filteredStages;
            
            // TEMPORARY: Show all stages for now
            this.state.stages = stages;
            this.state.loading = false;
            
            console.log('Displaying stages:', this.state.stages);
        } catch (error) {
            console.error('Error loading stages:', error);
            this.state.loading = false;
        }
    }
    
    async filterStagesByAccess(stages) {
        // Define stage access requirements - using exact group name patterns
        const stageAccessMap = {
            'Inquiry': ['admission / manager', 'admission / user'],
            'Admission': ['admission / manager', 'admission / user'],
            'Registration': ['admission / manager'],
            'Enrollment': ['openeducat / user'],
            'Academic Progress': ['assignment / manager', 'exam / manager', 'attendance / manager'],
            'Graduation': ['exam / manager'],
            'Core Module': ['administration / settings']
        };
        
        try {
            // Get current user info from session
            const session = await this.orm.call('res.users', 'context_get', []);
            const currentUserId = session.uid;
            
            console.log('Current user ID:', currentUserId);
            
            // Get current user's groups
            const userInfo = await this.orm.call('res.users', 'read', [[currentUserId]], {
                fields: ['groups_id', 'name']
            });
            
            if (!userInfo || userInfo.length === 0) {
                console.warn('Could not get user info, hiding all stages for security');
                return []; // Secure by default - hide all if can't verify
            }
            
            console.log('User info:', userInfo[0].name);
            
            const userGroupIds = userInfo[0].groups_id || [];
            console.log('User group IDs:', userGroupIds);
            
            // Get group complete names for user's groups
            const userGroups = await this.orm.searchRead(
                'res.groups',
                [['id', 'in', userGroupIds]],
                ['complete_name', 'name']
            );
            
            const userGroupNames = userGroups.map(g => g.complete_name.toLowerCase());
            
            console.log('=== USER ACCESS CONTROL DEBUG ===');
            console.log('User groups:', userGroupNames);
            
            // Check if user is system administrator (has access to everything)
            const isSystemAdmin = userGroupNames.some(name => 
                name.includes('administration / settings')
            );
            
            if (isSystemAdmin) {
                console.log('✓ User is system admin, showing all stages');
                return stages;
            }
            
            console.log('✗ User is NOT system admin, filtering stages...');
            
            // Filter stages based on access
            const accessibleStages = stages.filter(stage => {
                const requiredGroups = stageAccessMap[stage.name];
                
                // If no specific groups required, hide it (secure by default)
                if (!requiredGroups || requiredGroups.length === 0) {
                    console.log(`✗ Stage "${stage.name}" has no access rules, hiding`);
                    return false;
                }
                
                // Check if user has any of the required groups
                const hasAccess = requiredGroups.some(reqGroup => {
                    return userGroupNames.some(userGroup => {
                        return userGroup.includes(reqGroup);
                    });
                });
                
                const matchingGroups = userGroupNames.filter(ug => 
                    requiredGroups.some(rg => ug.includes(rg))
                );
                
                if (hasAccess) {
                    console.log(`✓ Stage "${stage.name}" - ACCESS GRANTED`, {
                        required: requiredGroups,
                        matched: matchingGroups
                    });
                } else {
                    console.log(`✗ Stage "${stage.name}" - ACCESS DENIED`, {
                        required: requiredGroups,
                        userHas: userGroupNames
                    });
                }
                
                return hasAccess;
            });
            
            console.log(`=== RESULT: Showing ${accessibleStages.length} of ${stages.length} stages ===`);
            console.log('Accessible stages:', accessibleStages.map(s => s.name));
            
            return accessibleStages;
        } catch (error) {
            console.error('❌ Error filtering stages by access:', error);
            console.error('Stack trace:', error.stack);
            return []; // Secure by default - hide all on error
        }
    }
    
    async openStage(stage) {
        // For stages without specific actions, open a generic view
        const stageActions = {
            'Inquiry': {
                type: 'ir.actions.act_window',
                name: 'Student Inquiries',
                res_model: 'op.admission',
                views: [[false, 'list'], [false, 'form']],
                domain: [['state', '=', 'draft']],
                context: { default_state: 'draft' },
                target: 'current'
            },
            'Registration': {
                type: 'ir.actions.act_window',
                name: 'Student Registration',
                res_model: 'op.student',
                views: [[false, 'list'], [false, 'form']],
                context: { default_active: true },
                target: 'current'
            },
            'Enrollment': {
                type: 'ir.actions.act_window',
                name: 'Student Enrollment',
                res_model: 'op.student',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            }
        };
        
        const defaultAction = stageActions[stage.name] || {
            type: 'ir.actions.act_window',
            name: stage.name,
            res_model: 'op.student',
            views: [[false, 'list'], [false, 'form']],
            target: 'current'
        };
        
        return this.actionService.doAction(defaultAction);
    }
    
    // Admission stage specific actions
    async openAdmissionRegisters(event) {
        event.stopPropagation(); // Prevent card click
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Admission Registers',
            res_model: 'op.admission.register',
            views: [[false, 'list'], [false, 'form']],
            target: 'current'
        });
    }
    
    async openAdmissionApplications(event) {
        event.stopPropagation(); // Prevent card click
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Admission Applications',
            res_model: 'op.admission',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', 'in', ['submit', 'confirm', 'admission']]],
            context: { default_state: 'submit' },
            target: 'current'
        });
    }
    
    async openAdmissionReport(event) {
        event.stopPropagation(); // Prevent card click
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Admission Report',
            res_model: 'op.admission',
            views: [[false, 'pivot'], [false, 'graph'], [false, 'list']],
            context: { 
                group_by: ['register_id', 'state'],
                search_default_group_by_register: 1,
                search_default_group_by_state: 1
            },
            target: 'current'
        });
    }

    async viewStages() {
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Workflow Stages',
            res_model: 'motakamel.workflow.stage',
            views: [[false, 'list'], [false, 'form']],
            domain: [['workflow_id', '=', this.workflowId]],
            context: { default_workflow_id: this.workflowId },
            target: 'current'
        });
    }

    async viewAnalytics() {
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Workflow Analytics',
            res_model: 'motakamel.workflow.analytics',
            views: [[false, 'list'], [false, 'form']],
            domain: [['workflow_id', '=', this.workflowId]],
            context: { default_workflow_id: this.workflowId },
            target: 'current'
        });
    }

    async viewTransitions() {
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Workflow Transitions',
            res_model: 'motakamel.workflow.transition',
            views: [[false, 'list'], [false, 'form']],
            domain: [['workflow_id', '=', this.workflowId]],
            context: { default_workflow_id: this.workflowId },
            target: 'current'
        });
    }

    async editWorkflow() {
        return this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Edit Workflow',
            res_model: 'motakamel.workflow',
            res_id: this.workflowId,
            views: [[false, 'form']],
            target: 'current'
        });
    }
}

WorkflowNavigation.template = "motakamel_workflow_dashboard.WorkflowNavigation";

registry.category("actions").add("motakamel_workflow_navigation", WorkflowNavigation);

