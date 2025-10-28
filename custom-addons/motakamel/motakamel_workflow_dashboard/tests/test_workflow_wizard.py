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


class TestWorkflowWizard(TransactionCase):
    """Test cases for workflow wizard functionality"""

    def setUp(self):
        super().setUp()
        self.Workflow = self.env['motakamel.workflow']
        self.WorkflowStage = self.env['motakamel.workflow.stage']
        self.WorkflowTransition = self.env['motakamel.workflow.transition']
        self.WorkflowSetupWizard = self.env['motakamel.workflow.setup.wizard']

    def test_wizard_creation(self):
        """Test wizard creation with valid data"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard_data = {
            'workflow_id': workflow.id,
            'setup_type': 'basic',
            'auto_create_stages': True,
            'auto_create_transitions': True,
            'include_analytics': True,
        }
        
        wizard = self.WorkflowSetupWizard.create(wizard_data)
        
        self.assertEqual(wizard.workflow_id, workflow)
        self.assertEqual(wizard.setup_type, 'basic')
        self.assertTrue(wizard.auto_create_stages)
        self.assertTrue(wizard.auto_create_transitions)
        self.assertTrue(wizard.include_analytics)

    def test_wizard_required_fields(self):
        """Test wizard creation with missing required fields"""
        with self.assertRaises(Exception):
            self.WorkflowSetupWizard.create({
                'setup_type': 'basic',
            })  # Missing workflow_id

    def test_wizard_setup_types(self):
        """Test different wizard setup types"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Test basic setup
        wizard_basic = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
            'auto_create_stages': True,
            'auto_create_transitions': True,
            'include_analytics': True,
        })
        
        self.assertEqual(wizard_basic.setup_type, 'basic')
        self.assertTrue(wizard_basic.auto_create_stages)
        
        # Test advanced setup
        wizard_advanced = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'advanced',
            'auto_create_stages': False,
            'auto_create_transitions': False,
            'include_analytics': False,
        })
        
        self.assertEqual(wizard_advanced.setup_type, 'advanced')
        self.assertFalse(wizard_advanced.auto_create_stages)
        
        # Test custom setup
        wizard_custom = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'custom',
            'custom_stages': '["Stage 1", "Stage 2", "Stage 3"]',
            'custom_transitions': '["Transition 1", "Transition 2"]',
        })
        
        self.assertEqual(wizard_custom.setup_type, 'custom')
        self.assertEqual(wizard_custom.custom_stages, '["Stage 1", "Stage 2", "Stage 3"]')

    def test_wizard_user_groups(self):
        """Test wizard user groups assignment"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Get some groups
        user_group = self.env.ref('base.group_user')
        system_group = self.env.ref('base.group_system')
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'advanced',
            'user_group_ids': [(6, 0, [user_group.id, system_group.id])],
        })
        
        # Verify group assignment
        self.assertIn(user_group, wizard.user_group_ids)
        self.assertIn(system_group, wizard.user_group_ids)
        self.assertEqual(len(wizard.user_group_ids), 2)

    def test_wizard_default_color(self):
        """Test wizard default color assignment"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'advanced',
            'default_color': '#ff5733',
        })
        
        self.assertEqual(wizard.default_color, '#ff5733')

    def test_wizard_action_setup_workflow(self):
        """Test wizard action_setup_workflow method"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
            'auto_create_stages': True,
            'auto_create_transitions': True,
            'include_analytics': True,
        })
        
        # Test setup workflow action
        result = wizard.action_setup_workflow()
        
        # Verify result
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertIn('Workflow setup completed', result['params']['message'])

    def test_wizard_basic_setup_creation(self):
        """Test basic setup workflow creation"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
            'auto_create_stages': True,
            'auto_create_transitions': True,
            'include_analytics': True,
        })
        
        # Execute setup
        wizard.action_setup_workflow()
        
        # Verify stages were created
        stages = self.WorkflowStage.search([('workflow_id', '=', workflow.id)])
        self.assertGreater(len(stages), 0)
        
        # Verify transitions were created
        transitions = self.WorkflowTransition.search([('workflow_id', '=', workflow.id)])
        self.assertGreater(len(transitions), 0)

    def test_wizard_advanced_setup_creation(self):
        """Test advanced setup workflow creation"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        user_group = self.env.ref('base.group_user')
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'advanced',
            'user_group_ids': [(6, 0, [user_group.id])],
            'default_color': '#3498db',
        })
        
        # Execute setup
        wizard.action_setup_workflow()
        
        # Verify workflow was updated
        workflow.refresh()
        self.assertEqual(workflow.color, '#3498db')
        self.assertIn(user_group, workflow.user_group_ids)

    def test_wizard_custom_setup_creation(self):
        """Test custom setup workflow creation"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'custom',
            'custom_stages': '["Custom Stage 1", "Custom Stage 2"]',
            'custom_transitions': '["Custom Transition 1"]',
        })
        
        # Execute setup
        wizard.action_setup_workflow()
        
        # Verify custom stages were created
        stages = self.WorkflowStage.search([('workflow_id', '=', workflow.id)])
        stage_names = [stage.name for stage in stages]
        
        self.assertIn('Custom Stage 1', stage_names)
        self.assertIn('Custom Stage 2', stage_names)

    def test_wizard_validation(self):
        """Test wizard validation rules"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Test valid wizard
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
        })
        self.assertTrue(wizard.id)
        
        # Test invalid setup type (should still work as no validation defined)
        wizard2 = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'invalid_type',
        })
        self.assertTrue(wizard2.id)

    def test_wizard_custom_fields_parsing(self):
        """Test wizard custom fields JSON parsing"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'custom',
            'custom_stages': '["Stage 1", "Stage 2", "Stage 3"]',
            'custom_transitions': '["Transition 1", "Transition 2"]',
        })
        
        # Test JSON parsing
        import json
        custom_stages = json.loads(wizard.custom_stages)
        custom_transitions = json.loads(wizard.custom_transitions)
        
        self.assertEqual(len(custom_stages), 3)
        self.assertEqual(len(custom_transitions), 2)
        self.assertIn('Stage 1', custom_stages)
        self.assertIn('Transition 1', custom_transitions)

    def test_wizard_error_handling(self):
        """Test wizard error handling"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
            'auto_create_stages': True,
        })
        
        # Test with invalid JSON in custom fields
        wizard.custom_stages = 'invalid json'
        
        # Should handle error gracefully
        try:
            wizard.action_setup_workflow()
        except Exception:
            # Expected to fail with invalid JSON
            pass

    def test_wizard_computed_fields(self):
        """Test wizard computed fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
        })
        
        # Test computed fields
        self.assertEqual(wizard.workflow_name, workflow.name)
        self.assertTrue(wizard.is_basic_setup)
        self.assertFalse(wizard.is_advanced_setup)
        self.assertFalse(wizard.is_custom_setup)

    def test_wizard_action_methods(self):
        """Test wizard action methods"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        wizard = self.WorkflowSetupWizard.create({
            'workflow_id': workflow.id,
            'setup_type': 'basic',
        })
        
        # Test action_view_workflow
        result = wizard.action_view_workflow()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow')
        self.assertEqual(result['res_id'], workflow.id)
        
        # Test action_cancel
        result = wizard.action_cancel()
        self.assertEqual(result['type'], 'ir.actions.act_window_close')
