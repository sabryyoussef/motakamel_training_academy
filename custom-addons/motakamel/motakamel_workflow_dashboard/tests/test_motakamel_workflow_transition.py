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


class TestMotakamelWorkflowTransition(TransactionCase):
    """Test cases for motakamel.workflow.transition model"""

    def setUp(self):
        super().setUp()
        self.Workflow = self.env['motakamel.workflow']
        self.WorkflowStage = self.env['motakamel.workflow.stage']
        self.WorkflowTransition = self.env['motakamel.workflow.transition']

    def test_transition_creation(self):
        """Test transition creation with valid data"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition_data = {
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'button_label': 'Complete',
            'condition': 'record.state == "draft"',
        }
        
        transition = self.WorkflowTransition.create(transition_data)
        
        self.assertEqual(transition.name, 'Test Transition')
        self.assertEqual(transition.workflow_id, workflow)
        self.assertEqual(transition.from_stage_id, stage1)
        self.assertEqual(transition.to_stage_id, stage2)
        self.assertEqual(transition.button_label, 'Complete')
        self.assertEqual(transition.condition, 'record.state == "draft"')
        self.assertTrue(transition.active)

    def test_transition_required_fields(self):
        """Test transition creation with missing required fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        with self.assertRaises(Exception):
            self.WorkflowTransition.create({
                'workflow_id': workflow.id,
                'from_stage_id': stage1.id,
                'to_stage_id': stage2.id,
            })  # Missing name

    def test_transition_workflow_relationship(self):
        """Test transition-workflow relationship"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        
        # Verify relationship
        self.assertEqual(transition.workflow_id, workflow)
        self.assertIn(transition, workflow.transition_ids)

    def test_transition_stage_relationships(self):
        """Test transition stage relationships"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        
        # Verify stage relationships
        self.assertEqual(transition.from_stage_id, stage1)
        self.assertEqual(transition.to_stage_id, stage2)
        
        # Verify next_stage_ids is updated
        self.assertIn(stage2, stage1.next_stage_ids)

    def test_transition_condition_evaluation(self):
        """Test transition condition evaluation"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'condition': 'True',  # Always true
        })
        
        # Test condition evaluation
        self.assertTrue(transition.evaluate_condition({'state': 'draft'}))
        
        # Test with false condition
        transition.condition = 'False'
        self.assertFalse(transition.evaluate_condition({'state': 'draft'}))

    def test_transition_button_label(self):
        """Test transition button label functionality"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'button_label': 'Complete Process',
        })
        
        # Test button label
        self.assertEqual(transition.button_label, 'Complete Process')
        
        # Test default button label
        transition.button_label = False
        self.assertEqual(transition.button_label, transition.name)

    def test_transition_deletion_cascade(self):
        """Test cascade deletion when workflow is deleted"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        
        transition_id = transition.id
        
        # Delete workflow
        workflow.unlink()
        
        # Verify transition is deleted
        self.assertFalse(self.WorkflowTransition.search([('id', '=', transition_id)]))

    def test_transition_search_and_filter(self):
        """Test transition search and filtering"""
        workflow1 = self.Workflow.create({
            'name': 'Workflow 1',
            'description': 'First workflow',
        })
        
        workflow2 = self.Workflow.create({
            'name': 'Workflow 2',
            'description': 'Second workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Stage 1',
            'workflow_id': workflow1.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Stage 2',
            'workflow_id': workflow2.id,
            'sequence': 10,
        })
        
        transition1 = self.WorkflowTransition.create({
            'name': 'Active Transition',
            'workflow_id': workflow1.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage1.id,
            'active': True,
        })
        
        transition2 = self.WorkflowTransition.create({
            'name': 'Inactive Transition',
            'workflow_id': workflow2.id,
            'from_stage_id': stage2.id,
            'to_stage_id': stage2.id,
            'active': False,
        })
        
        # Test search by name
        transitions = self.WorkflowTransition.search([('name', 'ilike', 'Active')])
        self.assertIn(transition1, transitions)
        self.assertNotIn(transition2, transitions)
        
        # Test search by workflow
        workflow1_transitions = self.WorkflowTransition.search([('workflow_id', '=', workflow1.id)])
        self.assertIn(transition1, workflow1_transitions)
        self.assertNotIn(transition2, workflow1_transitions)
        
        # Test search by active status
        active_transitions = self.WorkflowTransition.search([('active', '=', True)])
        self.assertIn(transition1, active_transitions)
        self.assertNotIn(transition2, active_transitions)

    def test_transition_computed_fields(self):
        """Test transition computed fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        
        # Test computed fields
        self.assertEqual(transition.workflow_name, workflow.name)
        self.assertEqual(transition.from_stage_name, stage1.name)
        self.assertEqual(transition.to_stage_name, stage2.name)

    def test_transition_action_methods(self):
        """Test transition action methods"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        
        # Test action_execute_transition
        result = transition.action_execute_transition()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')

    def test_transition_validation(self):
        """Test transition validation rules"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        # Test valid transition
        transition = self.WorkflowTransition.create({
            'name': 'Test Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        self.assertTrue(transition.id)
        
        # Test self-transition (should be allowed)
        self_transition = self.WorkflowTransition.create({
            'name': 'Self Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage1.id,
        })
        self.assertTrue(self_transition.id)

    def test_transition_sequence_ordering(self):
        """Test transition sequence ordering"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Start Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'End Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        transition1 = self.WorkflowTransition.create({
            'name': 'First Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'sequence': 20,
        })
        
        transition2 = self.WorkflowTransition.create({
            'name': 'Second Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'sequence': 10,
        })
        
        transition3 = self.WorkflowTransition.create({
            'name': 'Third Transition',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'sequence': 30,
        })
        
        # Test ordering
        transitions = self.WorkflowTransition.search([('workflow_id', '=', workflow.id)])
        self.assertEqual(transitions[0], transition2)  # sequence 10
        self.assertEqual(transitions[1], transition1)  # sequence 20
        self.assertEqual(transitions[2], transition3)  # sequence 30
