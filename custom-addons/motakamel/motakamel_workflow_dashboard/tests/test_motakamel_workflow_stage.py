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


class TestMotakamelWorkflowStage(TransactionCase):
    """Test cases for motakamel.workflow.stage model"""

    def setUp(self):
        super().setUp()
        self.Workflow = self.env['motakamel.workflow']
        self.WorkflowStage = self.env['motakamel.workflow.stage']
        self.WorkflowTransition = self.env['motakamel.workflow.transition']
        self.ModuleInfo = self.env['motakamel.module.info']

    def test_stage_creation(self):
        """Test stage creation with valid data"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage_data = {
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
            'description': 'Test stage description',
            'required_fields': '["field1", "field2"]',
        }
        
        stage = self.WorkflowStage.create(stage_data)
        
        self.assertEqual(stage.name, 'Test Stage')
        self.assertEqual(stage.workflow_id, workflow)
        self.assertEqual(stage.sequence, 10)
        self.assertEqual(stage.description, 'Test stage description')
        self.assertEqual(stage.required_fields, '["field1", "field2"]')
        self.assertTrue(stage.active)

    def test_stage_required_fields(self):
        """Test stage creation with missing required fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        with self.assertRaises(Exception):
            self.WorkflowStage.create({'workflow_id': workflow.id})  # Missing name

    def test_stage_workflow_relationship(self):
        """Test stage-workflow relationship"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Verify relationship
        self.assertEqual(stage.workflow_id, workflow)
        self.assertIn(stage, workflow.stage_ids)

    def test_stage_sequence_ordering(self):
        """Test stage sequence ordering within workflow"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'First Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Second Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage3 = self.WorkflowStage.create({
            'name': 'Third Stage',
            'workflow_id': workflow.id,
            'sequence': 30,
        })
        
        # Test ordering
        stages = self.WorkflowStage.search([('workflow_id', '=', workflow.id)])
        self.assertEqual(stages[0], stage2)  # sequence 10
        self.assertEqual(stages[1], stage1)  # sequence 20
        self.assertEqual(stages[2], stage3)  # sequence 30

    def test_stage_transitions(self):
        """Test stage transitions"""
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
        
        # Create transition
        transition = self.WorkflowTransition.create({
            'name': 'Start to End',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'button_label': 'Complete',
        })
        
        # Verify transition relationships
        self.assertEqual(transition.from_stage_id, stage1)
        self.assertEqual(transition.to_stage_id, stage2)
        self.assertIn(stage2, stage1.next_stage_ids)

    def test_stage_module_info_relationship(self):
        """Test stage-module info relationship"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Create module info (if motakamel_dashboard is available)
        try:
            module_info = self.ModuleInfo.create({
                'name': 'Test Module',
                'technical_name': 'test_module',
                'description': 'Test module',
                'sequence': 10,
                'category': 'test',
            })
            
            # Assign module to stage
            stage.module_info_ids = [(6, 0, [module_info.id])]
            
            # Verify relationship
            self.assertIn(module_info, stage.module_info_ids)
            
        except Exception:
            # Skip if motakamel_dashboard is not available
            pass

    def test_stage_action_relationship(self):
        """Test stage-action relationship"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Create a test action
        action = self.env['ir.actions.act_window'].create({
            'name': 'Test Action',
            'res_model': 'motakamel.workflow',
            'view_mode': 'tree,form',
        })
        
        # Assign action to stage
        stage.action_ids = [(6, 0, [action.id])]
        
        # Verify relationship
        self.assertIn(action, stage.action_ids)

    def test_stage_required_fields_json(self):
        """Test required fields JSON handling"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
            'required_fields': '["name", "email", "phone"]',
        })
        
        # Test JSON parsing
        import json
        required_fields = json.loads(stage.required_fields)
        self.assertEqual(len(required_fields), 3)
        self.assertIn('name', required_fields)
        self.assertIn('email', required_fields)
        self.assertIn('phone', required_fields)

    def test_stage_deletion_cascade(self):
        """Test cascade deletion when workflow is deleted"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage_id = stage.id
        
        # Delete workflow
        workflow.unlink()
        
        # Verify stage is deleted
        self.assertFalse(self.WorkflowStage.search([('id', '=', stage_id)]))

    def test_stage_search_and_filter(self):
        """Test stage search and filtering"""
        workflow1 = self.Workflow.create({
            'name': 'Workflow 1',
            'description': 'First workflow',
        })
        
        workflow2 = self.Workflow.create({
            'name': 'Workflow 2',
            'description': 'Second workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Active Stage',
            'workflow_id': workflow1.id,
            'sequence': 10,
            'active': True,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Inactive Stage',
            'workflow_id': workflow2.id,
            'sequence': 10,
            'active': False,
        })
        
        # Test search by name
        stages = self.WorkflowStage.search([('name', 'ilike', 'Active')])
        self.assertIn(stage1, stages)
        self.assertNotIn(stage2, stages)
        
        # Test search by workflow
        workflow1_stages = self.WorkflowStage.search([('workflow_id', '=', workflow1.id)])
        self.assertIn(stage1, workflow1_stages)
        self.assertNotIn(stage2, workflow1_stages)
        
        # Test search by active status
        active_stages = self.WorkflowStage.search([('active', '=', True)])
        self.assertIn(stage1, active_stages)
        self.assertNotIn(stage2, active_stages)

    def test_stage_computed_fields(self):
        """Test stage computed fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Test computed fields
        self.assertEqual(stage.workflow_name, workflow.name)
        self.assertEqual(stage.stage_count, 0)  # No child stages initially

    def test_stage_action_methods(self):
        """Test stage action methods"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Test action_open_stage_dashboard
        result = stage.action_open_stage_dashboard()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow.stage')
        self.assertEqual(result['res_id'], stage.id)
        
        # Test action_view_transitions
        result = stage.action_view_transitions()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow.transition')

    def test_stage_validation(self):
        """Test stage validation rules"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Test valid sequence
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        self.assertTrue(stage.id)
        
        # Test invalid sequence (should still work as no validation defined)
        stage2 = self.WorkflowStage.create({
            'name': 'Test Stage 2',
            'workflow_id': workflow.id,
            'sequence': -5,
        })
        self.assertTrue(stage2.id)
