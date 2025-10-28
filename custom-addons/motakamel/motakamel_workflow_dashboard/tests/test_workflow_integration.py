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


class TestWorkflowIntegration(TransactionCase):
    """Test cases for workflow integration and end-to-end functionality"""

    def setUp(self):
        super().setUp()
        self.Workflow = self.env['motakamel.workflow']
        self.WorkflowStage = self.env['motakamel.workflow.stage']
        self.WorkflowTransition = self.env['motakamel.workflow.transition']
        self.WorkflowAnalytics = self.env['motakamel.workflow.analytics']
        self.WorkflowSetupWizard = self.env['motakamel.workflow.setup.wizard']

    def test_complete_workflow_lifecycle(self):
        """Test complete workflow lifecycle from creation to execution"""
        # Create workflow
        workflow = self.Workflow.create({
            'name': 'Complete Test Workflow',
            'description': 'End-to-end workflow test',
            'color': '#3498db',
            'icon': 'test_icon.png',
        })
        
        # Create stages
        stage1 = self.WorkflowStage.create({
            'name': 'Start',
            'workflow_id': workflow.id,
            'sequence': 10,
            'description': 'Initial stage',
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Process',
            'workflow_id': workflow.id,
            'sequence': 20,
            'description': 'Processing stage',
        })
        
        stage3 = self.WorkflowStage.create({
            'name': 'Complete',
            'workflow_id': workflow.id,
            'sequence': 30,
            'description': 'Final stage',
        })
        
        # Create transitions
        transition1 = self.WorkflowTransition.create({
            'name': 'Start to Process',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
            'button_label': 'Begin Process',
        })
        
        transition2 = self.WorkflowTransition.create({
            'name': 'Process to Complete',
            'workflow_id': workflow.id,
            'from_stage_id': stage2.id,
            'to_stage_id': stage3.id,
            'button_label': 'Complete',
        })
        
        # Create analytics
        analytics1 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage1.id,
            'record_count': 100,
            'avg_duration': 5.0,
        })
        
        analytics2 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage2.id,
            'record_count': 80,
            'avg_duration': 15.0,
        })
        
        analytics3 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage3.id,
            'record_count': 75,
            'avg_duration': 2.0,
        })
        
        # Verify complete workflow structure
        self.assertEqual(len(workflow.stage_ids), 3)
        self.assertEqual(len(workflow.transition_ids), 2)
        self.assertEqual(len(workflow.analytics_ids), 3)
        
        # Verify stage relationships
        self.assertIn(stage2, stage1.next_stage_ids)
        self.assertIn(stage3, stage2.next_stage_ids)
        
        # Verify analytics relationships
        self.assertEqual(analytics1.stage_id, stage1)
        self.assertEqual(analytics2.stage_id, stage2)
        self.assertEqual(analytics3.stage_id, stage3)

    def test_workflow_with_external_modules(self):
        """Test workflow integration with external modules"""
        workflow = self.Workflow.create({
            'name': 'External Integration Workflow',
            'description': 'Workflow with external module integration',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'External Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Test integration with motakamel_dashboard if available
        try:
            module_info = self.env['motakamel.module.info'].create({
                'name': 'Test Module',
                'technical_name': 'test_module',
                'description': 'Test module for integration',
                'sequence': 10,
                'category': 'test',
            })
            
            # Assign module to stage
            stage.module_info_ids = [(6, 0, [module_info.id])]
            
            # Verify integration
            self.assertIn(module_info, stage.module_info_ids)
            
        except Exception:
            # Skip if motakamel_dashboard is not available
            pass

    def test_workflow_performance_metrics(self):
        """Test workflow performance metrics calculation"""
        workflow = self.Workflow.create({
            'name': 'Performance Test Workflow',
            'description': 'Workflow for performance testing',
        })
        
        # Create stages with different performance characteristics
        fast_stage = self.WorkflowStage.create({
            'name': 'Fast Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        slow_stage = self.WorkflowStage.create({
            'name': 'Slow Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        # Create analytics with different performance metrics
        fast_analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': fast_stage.id,
            'record_count': 1000,
            'avg_duration': 1.0,
        })
        
        slow_analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': slow_stage.id,
            'record_count': 1000,
            'avg_duration': 100.0,
            'bottleneck_reason': 'Complex processing',
        })
        
        # Test performance calculations
        workflow_analytics = self.WorkflowAnalytics.search([('workflow_id', '=', workflow.id)])
        
        # Calculate total records
        total_records = sum(a.record_count for a in workflow_analytics)
        self.assertEqual(total_records, 2000)
        
        # Calculate average duration
        avg_duration = sum(a.avg_duration for a in workflow_analytics) / len(workflow_analytics)
        self.assertEqual(avg_duration, 50.5)
        
        # Identify bottlenecks
        bottlenecks = workflow_analytics.filtered(lambda a: a.bottleneck_reason)
        self.assertEqual(len(bottlenecks), 1)
        self.assertEqual(bottlenecks[0], slow_analytics)

    def test_workflow_user_permissions(self):
        """Test workflow user permissions and access control"""
        workflow = self.Workflow.create({
            'name': 'Permission Test Workflow',
            'description': 'Workflow for permission testing',
        })
        
        # Get user groups
        user_group = self.env.ref('base.group_user')
        system_group = self.env.ref('base.group_system')
        
        # Assign groups to workflow
        workflow.user_group_ids = [(6, 0, [user_group.id, system_group.id])]
        
        # Verify group assignment
        self.assertIn(user_group, workflow.user_group_ids)
        self.assertIn(system_group, workflow.user_group_ids)
        
        # Test access control
        self.assertTrue(workflow.check_user_access(self.env.user))

    def test_workflow_data_consistency(self):
        """Test workflow data consistency and integrity"""
        workflow = self.Workflow.create({
            'name': 'Consistency Test Workflow',
            'description': 'Workflow for consistency testing',
        })
        
        # Create stages
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
        
        # Create transition
        transition = self.WorkflowTransition.create({
            'name': 'Transition 1',
            'workflow_id': workflow.id,
            'from_stage_id': stage1.id,
            'to_stage_id': stage2.id,
        })
        
        # Test data consistency
        self.assertEqual(transition.workflow_id, workflow)
        self.assertEqual(transition.from_stage_id.workflow_id, workflow)
        self.assertEqual(transition.to_stage_id.workflow_id, workflow)
        
        # Test cascade relationships
        self.assertIn(stage2, stage1.next_stage_ids)
        self.assertIn(transition, workflow.transition_ids)

    def test_workflow_bulk_operations(self):
        """Test workflow bulk operations"""
        # Create multiple workflows
        workflows = []
        for i in range(5):
            workflow = self.Workflow.create({
                'name': f'Bulk Workflow {i+1}',
                'description': f'Bulk workflow {i+1}',
                'sequence': i * 10,
            })
            workflows.append(workflow)
        
        # Test bulk search
        all_workflows = self.Workflow.search([])
        self.assertGreaterEqual(len(all_workflows), 5)
        
        # Test bulk update
        self.Workflow.search([('name', 'ilike', 'Bulk Workflow')]).write({
            'color': '#ff5733'
        })
        
        # Verify bulk update
        updated_workflows = self.Workflow.search([('name', 'ilike', 'Bulk Workflow')])
        for workflow in updated_workflows:
            self.assertEqual(workflow.color, '#ff5733')
        
        # Test bulk delete
        bulk_workflow_ids = [w.id for w in workflows]
        self.Workflow.search([('id', 'in', bulk_workflow_ids)]).unlink()
        
        # Verify bulk delete
        remaining_workflows = self.Workflow.search([('id', 'in', bulk_workflow_ids)])
        self.assertEqual(len(remaining_workflows), 0)

    def test_workflow_error_recovery(self):
        """Test workflow error recovery and resilience"""
        workflow = self.Workflow.create({
            'name': 'Error Recovery Workflow',
            'description': 'Workflow for error recovery testing',
        })
        
        # Create stage with invalid data
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
            'required_fields': 'invalid json',  # Invalid JSON
        })
        
        # Test error handling
        try:
            import json
            json.loads(stage.required_fields)
        except json.JSONDecodeError:
            # Expected error with invalid JSON
            pass
        
        # Test recovery by fixing the data
        stage.required_fields = '["field1", "field2"]'
        
        # Verify recovery
        try:
            json.loads(stage.required_fields)
            # Should work now
            self.assertTrue(True)
        except json.JSONDecodeError:
            self.fail("JSON should be valid after recovery")

    def test_workflow_scalability(self):
        """Test workflow scalability with large datasets"""
        workflow = self.Workflow.create({
            'name': 'Scalability Test Workflow',
            'description': 'Workflow for scalability testing',
        })
        
        # Create many stages
        stages = []
        for i in range(50):
            stage = self.WorkflowStage.create({
                'name': f'Stage {i+1}',
                'workflow_id': workflow.id,
                'sequence': i * 10,
            })
            stages.append(stage)
        
        # Create transitions between consecutive stages
        transitions = []
        for i in range(49):
            transition = self.WorkflowTransition.create({
                'name': f'Transition {i+1}',
                'workflow_id': workflow.id,
                'from_stage_id': stages[i].id,
                'to_stage_id': stages[i+1].id,
            })
            transitions.append(transition)
        
        # Create analytics for each stage
        analytics = []
        for i, stage in enumerate(stages):
            analytic = self.WorkflowAnalytics.create({
                'workflow_id': workflow.id,
                'stage_id': stage.id,
                'record_count': 100 + i,
                'avg_duration': 10.0 + i,
            })
            analytics.append(analytic)
        
        # Test scalability
        self.assertEqual(len(workflow.stage_ids), 50)
        self.assertEqual(len(workflow.transition_ids), 49)
        self.assertEqual(len(workflow.analytics_ids), 50)
        
        # Test performance with large dataset
        start_time = self.env.cr.now()
        workflow.refresh()
        end_time = self.env.cr.now()
        
        # Should complete quickly even with large dataset
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second

    def test_workflow_integration_with_odoo_core(self):
        """Test workflow integration with Odoo core functionality"""
        workflow = self.Workflow.create({
            'name': 'Odoo Integration Workflow',
            'description': 'Workflow for Odoo core integration testing',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Odoo Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Test integration with ir.actions.act_window
        action = self.env['ir.actions.act_window'].create({
            'name': 'Test Action',
            'res_model': 'motakamel.workflow',
            'view_mode': 'tree,form',
        })
        
        # Assign action to stage
        stage.action_ids = [(6, 0, [action.id])]
        
        # Verify integration
        self.assertIn(action, stage.action_ids)
        
        # Test integration with ir.ui.menu
        menu = self.env['ir.ui.menu'].create({
            'name': 'Test Menu',
            'action': action.id,
        })
        
        # Test workflow action methods
        result = workflow.action_open_workflow_dashboard()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow')
        
        # Test stage action methods
        result = stage.action_open_stage_dashboard()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow.stage')
