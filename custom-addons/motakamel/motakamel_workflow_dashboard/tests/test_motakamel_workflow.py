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

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMotakamelWorkflow(TransactionCase):
    """Test cases for motakamel.workflow model"""

    def setUp(self):
        super().setUp()
        self.Workflow = self.env['motakamel.workflow']
        self.WorkflowStage = self.env['motakamel.workflow.stage']
        self.WorkflowTransition = self.env['motakamel.workflow.transition']
        self.WorkflowAnalytics = self.env['motakamel.workflow.analytics']

    def test_workflow_creation(self):
        """Test workflow creation with valid data"""
        workflow_data = {
            'name': 'Test Workflow',
            'description': 'Test workflow description',
            'sequence': 10,
            'color': '#3498db',
            'icon': 'test_icon.png',
        }
        
        workflow = self.Workflow.create(workflow_data)
        
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertEqual(workflow.description, 'Test workflow description')
        self.assertEqual(workflow.sequence, 10)
        self.assertEqual(workflow.color, '#3498db')
        self.assertEqual(workflow.icon, 'test_icon.png')
        self.assertTrue(workflow.active)

    def test_workflow_required_fields(self):
        """Test workflow creation with missing required fields"""
        with self.assertRaises(Exception):
            self.Workflow.create({'description': 'Missing name'})

    def test_workflow_computed_fields(self):
        """Test computed fields calculation"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Initially no stages
        self.assertEqual(workflow.stage_count, 0)
        self.assertEqual(workflow.progress_percentage, 0)
        
        # Add stages
        stage1 = self.WorkflowStage.create({
            'name': 'Stage 1',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Stage 2',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        # Refresh to recompute
        workflow.refresh()
        self.assertEqual(workflow.stage_count, 2)

    def test_workflow_action_methods(self):
        """Test workflow action methods"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Test action_open_workflow_dashboard
        result = workflow.action_open_workflow_dashboard()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow')
        self.assertEqual(result['res_id'], workflow.id)
        
        # Test action_view_stages
        result = workflow.action_view_stages()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow.stage')
        
        # Test action_view_analytics
        result = workflow.action_view_analytics()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow.analytics')

    def test_workflow_with_stages_and_transitions(self):
        """Test workflow with stages and transitions"""
        workflow = self.Workflow.create({
            'name': 'Complete Workflow',
            'description': 'Workflow with stages and transitions',
        })
        
        # Create stages
        stage1 = self.WorkflowStage.create({
            'name': 'Start',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Process',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        stage3 = self.WorkflowStage.create({
            'name': 'End',
            'workflow_id': workflow.id,
            'sequence': 30,
        })
        
        # Create transitions
        transition1 = self.WorkflowTransition.create({
            'name': 'Start to Process',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'button_label': 'Start Process',
        })
        
        transition2 = self.WorkflowTransition.create({
            'name': 'Process to End',
            'workflow_id': workflow.id,
            'from_stage_id': stage2.id,
            'to_stage_id': stage3.id,
            'button_label': 'Complete',
        })
        
        # Verify relationships
        self.assertEqual(len(workflow.stage_ids), 3)
        self.assertEqual(len(workflow.transition_ids), 2)
        
        # Verify stage relationships
        self.assertIn(stage2, stage1.next_stage_ids)
        self.assertIn(stage3, stage2.next_stage_ids)

    def test_workflow_analytics_integration(self):
        """Test workflow analytics integration"""
        workflow = self.Workflow.create({
            'name': 'Analytics Workflow',
            'description': 'Workflow for analytics testing',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Create analytics
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage.id,
            'record_count': 100,
            'avg_duration': 24.5,
        })
        
        # Verify analytics relationship
        self.assertIn(analytics, workflow.analytics_ids)
        self.assertEqual(analytics.workflow_id, workflow)
        self.assertEqual(analytics.stage_id, stage)

    def test_workflow_deletion_cascade(self):
        """Test cascade deletion of related records"""
        workflow = self.Workflow.create({
            'name': 'Cascade Test Workflow',
            'description': 'Workflow for cascade testing',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage.id,
            'to_stage_id': stage.id,
            'button_label': 'Test',
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage.id,
        })
        
        # Delete workflow
        workflow_id = workflow.id
        workflow.unlink()
        
        # Verify cascade deletion
        self.assertFalse(self.WorkflowStage.search([('workflow_id', '=', workflow_id)]))
        self.assertFalse(self.WorkflowTransition.search([('workflow_id', '=', workflow_id)]))
        self.assertFalse(self.WorkflowAnalytics.search([('workflow_id', '=', workflow_id)]))

    def test_workflow_search_and_filter(self):
        """Test workflow search and filtering"""
        workflow1 = self.Workflow.create({
            'name': 'Active Workflow',
            'description': 'Active workflow',
            'active': True,
        })
        
        workflow2 = self.Workflow.create({
            'name': 'Inactive Workflow',
            'description': 'Inactive workflow',
            'active': False,
        })
        
        # Test search by name
        workflows = self.Workflow.search([('name', 'ilike', 'Active')])
        self.assertIn(workflow1, workflows)
        self.assertNotIn(workflow2, workflows)
        
        # Test search by active status
        active_workflows = self.Workflow.search([('active', '=', True)])
        self.assertIn(workflow1, active_workflows)
        self.assertNotIn(workflow2, active_workflows)

    def test_workflow_sequence_ordering(self):
        """Test workflow sequence ordering"""
        workflow1 = self.Workflow.create({
            'name': 'First Workflow',
            'sequence': 10,
        })
        
        workflow2 = self.Workflow.create({
            'name': 'Second Workflow',
            'sequence': 20,
        })
        
        workflow3 = self.Workflow.create({
            'name': 'Third Workflow',
            'sequence': 5,
        })
        
        # Test ordering
        workflows = self.Workflow.search([])
        self.assertEqual(workflows[0], workflow3)  # sequence 5
        self.assertEqual(workflows[1], workflow1)   # sequence 10
        self.assertEqual(workflows[2], workflow2)   # sequence 20

    def test_workflow_user_groups(self):
        """Test workflow user groups assignment"""
        workflow = self.Workflow.create({
            'name': 'Group Test Workflow',
            'description': 'Workflow for group testing',
        })
        
        # Get some groups
        user_group = self.env.ref('base.group_user')
        system_group = self.env.ref('base.group_system')
        
        # Assign groups
        workflow.user_group_ids = [(6, 0, [user_group.id, system_group.id])]
        
        # Verify assignment
        self.assertIn(user_group, workflow.user_group_ids)
        self.assertIn(system_group, workflow.user_group_ids)
        self.assertEqual(len(workflow.user_group_ids), 2)
