###############################################################################
#
#    Motakamel Workflow Dashboard
#    Copyright (C) 2024 Motakamel Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api


class WorkflowSetupWizard(models.TransientModel):
    _name = 'motakamel.workflow.setup.wizard'
    _description = 'Workflow Setup Wizard'

    workflow_id = fields.Many2one('motakamel.workflow', string='Workflow', required=True)
    setup_type = fields.Selection([
        ('basic', 'Basic Setup'),
        ('advanced', 'Advanced Setup'),
        ('custom', 'Custom Setup'),
    ], string='Setup Type', default='basic', required=True)
    
    # Basic setup fields
    auto_create_stages = fields.Boolean(string='Auto Create Stages', default=True)
    auto_create_transitions = fields.Boolean(string='Auto Create Transitions', default=True)
    include_analytics = fields.Boolean(string='Include Analytics', default=True)
    
    # Advanced setup fields
    user_group_ids = fields.Many2many('res.groups', string='User Groups')
    default_color = fields.Char(string='Default Color', default='#3498db')
    
    # Custom setup fields
    custom_stages = fields.Text(string='Custom Stages', help='JSON format: [{"name": "Stage Name", "sequence": 10}]')
    custom_transitions = fields.Text(string='Custom Transitions', help='JSON format: [{"from": "Stage1", "to": "Stage2"}]')

    def action_setup_workflow(self):
        """Setup the workflow based on selected options"""
        self.ensure_one()
        
        if self.setup_type == 'basic':
            self._setup_basic_workflow()
        elif self.setup_type == 'advanced':
            self._setup_advanced_workflow()
        elif self.setup_type == 'custom':
            self._setup_custom_workflow()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Workflow Setup Complete',
                'message': f'Workflow {self.workflow_id.name} has been set up successfully.',
                'type': 'success',
            }
        }

    def _setup_basic_workflow(self):
        """Setup basic workflow with default stages"""
        if self.auto_create_stages:
            # Create basic stages based on workflow type
            stage_data = self._get_default_stages()
            for stage_info in stage_data:
                self.env['motakamel.workflow.stage'].create({
                    'name': stage_info['name'],
                    'workflow_id': self.workflow_id.id,
                    'sequence': stage_info['sequence'],
                    'description': stage_info.get('description', ''),
                    'color': stage_info.get('color', self.default_color),
                })
        
        if self.auto_create_transitions:
            self._create_default_transitions()
        
        if self.include_analytics:
            self._setup_analytics()

    def _setup_advanced_workflow(self):
        """Setup advanced workflow with custom options"""
        self._setup_basic_workflow()
        
        # Set user groups
        if self.user_group_ids:
            self.workflow_id.user_group_ids = self.user_group_ids
        
        # Set default color
        if self.default_color:
            self.workflow_id.color = self.default_color

    def _setup_custom_workflow(self):
        """Setup custom workflow with user-defined stages and transitions"""
        import json
        
        # Create custom stages
        if self.custom_stages:
            try:
                stages_data = json.loads(self.custom_stages)
                for stage_info in stages_data:
                    self.env['motakamel.workflow.stage'].create({
                        'name': stage_info['name'],
                        'workflow_id': self.workflow_id.id,
                        'sequence': stage_info.get('sequence', 10),
                        'description': stage_info.get('description', ''),
                        'color': stage_info.get('color', self.default_color),
                    })
            except json.JSONDecodeError:
                pass
        
        # Create custom transitions
        if self.custom_transitions:
            try:
                transitions_data = json.loads(self.custom_transitions)
                for transition_info in transitions_data:
                    from_stage = self.env['motakamel.workflow.stage'].search([
                        ('workflow_id', '=', self.workflow_id.id),
                        ('name', '=', transition_info['from'])
                    ], limit=1)
                    to_stage = self.env['motakamel.workflow.stage'].search([
                        ('workflow_id', '=', self.workflow_id.id),
                        ('name', '=', transition_info['to'])
                    ], limit=1)
                    
                    if from_stage and to_stage:
                        self.env['motakamel.workflow.transition'].create({
                            'name': transition_info.get('name', f"{transition_info['from']} to {transition_info['to']}"),
                            'workflow_id': self.workflow_id.id,
                            'from_stage_id': from_stage.id,
                            'to_stage_id': to_stage.id,
                            'button_label': transition_info.get('button_label', 'Continue'),
                            'sequence': transition_info.get('sequence', 10),
                        })
            except json.JSONDecodeError:
                pass

    def _get_default_stages(self):
        """Get default stages based on workflow type"""
        workflow_name = self.workflow_id.name.lower()
        
        if 'student' in workflow_name:
            return [
                {'name': 'Inquiry', 'sequence': 10, 'color': '#e74c3c'},
                {'name': 'Admission', 'sequence': 20, 'color': '#f39c12'},
                {'name': 'Registration', 'sequence': 30, 'color': '#2ecc71'},
                {'name': 'Enrollment', 'sequence': 40, 'color': '#9b59b6'},
                {'name': 'Academic Progress', 'sequence': 50, 'color': '#1abc9c'},
                {'name': 'Graduation', 'sequence': 60, 'color': '#34495e'},
            ]
        elif 'academic' in workflow_name:
            return [
                {'name': 'Planning', 'sequence': 10, 'color': '#e74c3c'},
                {'name': 'Scheduling', 'sequence': 20, 'color': '#f39c12'},
                {'name': 'Execution', 'sequence': 30, 'color': '#2ecc71'},
                {'name': 'Assessment', 'sequence': 40, 'color': '#9b59b6'},
                {'name': 'Results', 'sequence': 50, 'color': '#1abc9c'},
            ]
        elif 'financial' in workflow_name:
            return [
                {'name': 'Setup', 'sequence': 10, 'color': '#e74c3c'},
                {'name': 'Collection', 'sequence': 20, 'color': '#f39c12'},
                {'name': 'Processing', 'sequence': 30, 'color': '#2ecc71'},
                {'name': 'Reporting', 'sequence': 40, 'color': '#9b59b6'},
            ]
        else:
            return [
                {'name': 'Start', 'sequence': 10, 'color': '#e74c3c'},
                {'name': 'Process', 'sequence': 20, 'color': '#f39c12'},
                {'name': 'Complete', 'sequence': 30, 'color': '#2ecc71'},
            ]

    def _create_default_transitions(self):
        """Create default transitions between stages"""
        stages = self.env['motakamel.workflow.stage'].search([
            ('workflow_id', '=', self.workflow_id.id)
        ], order='sequence')
        
        for i in range(len(stages) - 1):
            self.env['motakamel.workflow.transition'].create({
                'name': f"{stages[i].name} to {stages[i+1].name}",
                'workflow_id': self.workflow_id.id,
                'from_stage_id': stages[i].id,
                'to_stage_id': stages[i+1].id,
                'button_label': f'Go to {stages[i+1].name}',
                'sequence': (i + 1) * 10,
            })

    def _setup_analytics(self):
        """Setup analytics for the workflow"""
        stages = self.env['motakamel.workflow.stage'].search([
            ('workflow_id', '=', self.workflow_id.id)
        ])
        
        for stage in stages:
            self.env['motakamel.workflow.analytics'].create({
                'workflow_id': self.workflow_id.id,
                'stage_id': stage.id,
                'record_count': 0,
                'avg_duration': 0.0,
            })
