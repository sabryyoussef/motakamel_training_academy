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


class TestMotakamelWorkflowAnalytics(TransactionCase):
    """Test cases for motakamel.workflow.analytics model"""

    def setUp(self):
        super().setUp()
        self.Workflow = self.env['motakamel.workflow']
        self.WorkflowStage = self.env['motakamel.workflow.stage']
        self.WorkflowAnalytics = self.env['motakamel.workflow.analytics']

    def test_analytics_creation(self):
        """Test analytics creation with valid data"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        analytics_data = {
            'workflow_id': workflow.id,
            'stage_id': stage.id,
            'record_count': 100,
            'avg_duration': 24.5,
            'bottleneck_reason': 'High volume',
        }
        
        analytics = self.WorkflowAnalytics.create(analytics_data)
        
        self.assertEqual(analytics.workflow_id, workflow)
        self.assertEqual(analytics.stage_id, stage)
        self.assertEqual(analytics.record_count, 100)
        self.assertEqual(analytics.avg_duration, 24.5)
        self.assertEqual(analytics.bottleneck_reason, 'High volume')
        self.assertTrue(analytics.last_update)

    def test_analytics_required_fields(self):
        """Test analytics creation with missing required fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        with self.assertRaises(Exception):
            self.WorkflowAnalytics.create({
                'stage_id': workflow.id,  # Missing workflow_id
            })

    def test_analytics_workflow_relationship(self):
        """Test analytics-workflow relationship"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
        })
        
        # Verify relationship
        self.assertEqual(analytics.workflow_id, workflow)
        self.assertIn(analytics, workflow.analytics_ids)

    def test_analytics_stage_relationship(self):
        """Test analytics-stage relationship"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage.id,
        })
        
        # Verify relationship
        self.assertEqual(analytics.stage_id, stage)

    def test_analytics_computed_fields(self):
        """Test analytics computed fields"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage.id,
            'record_count': 100,
            'avg_duration': 24.5,
        })
        
        # Test computed fields
        self.assertEqual(analytics.workflow_name, workflow.name)
        self.assertEqual(analytics.stage_name, stage.name)
        self.assertEqual(analytics.efficiency_score, 100)  # Default calculation

    def test_analytics_efficiency_calculation(self):
        """Test analytics efficiency calculation"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage = self.WorkflowStage.create({
            'name': 'Test Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        # Test different efficiency scenarios
        analytics1 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage.id,
            'record_count': 100,
            'avg_duration': 1.0,  # Very fast
        })
        
        analytics2 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage.id,
            'record_count': 50,
            'avg_duration': 100.0,  # Very slow
        })
        
        # Test efficiency calculations
        self.assertGreater(analytics1.efficiency_score, analytics2.efficiency_score)

    def test_analytics_deletion_cascade(self):
        """Test cascade deletion when workflow is deleted"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
        })
        
        analytics_id = analytics.id
        
        # Delete workflow
        workflow.unlink()
        
        # Verify analytics is deleted
        self.assertFalse(self.WorkflowAnalytics.search([('id', '=', analytics_id)]))

    def test_analytics_search_and_filter(self):
        """Test analytics search and filtering"""
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
        
        analytics1 = self.WorkflowAnalytics.create({
            'workflow_id': workflow1.id,
            'stage_id': stage1.id,
            'record_count': 100,
        })
        
        analytics2 = self.WorkflowAnalytics.create({
            'workflow_id': workflow2.id,
            'stage_id': stage2.id,
            'record_count': 50,
        })
        
        # Test search by workflow
        workflow1_analytics = self.WorkflowAnalytics.search([('workflow_id', '=', workflow1.id)])
        self.assertIn(analytics1, workflow1_analytics)
        self.assertNotIn(analytics2, workflow1_analytics)
        
        # Test search by stage
        stage1_analytics = self.WorkflowAnalytics.search([('stage_id', '=', stage1.id)])
        self.assertIn(analytics1, stage1_analytics)
        self.assertNotIn(analytics2, stage1_analytics)
        
        # Test search by record count
        high_count_analytics = self.WorkflowAnalytics.search([('record_count', '>', 75)])
        self.assertIn(analytics1, high_count_analytics)
        self.assertNotIn(analytics2, high_count_analytics)

    def test_analytics_update_tracking(self):
        """Test analytics update tracking"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'record_count': 100,
        })
        
        initial_update = analytics.last_update
        
        # Update analytics
        analytics.write({
            'record_count': 150,
            'avg_duration': 30.0,
        })
        
        # Verify last_update was updated
        self.assertGreater(analytics.last_update, initial_update)

    def test_analytics_action_methods(self):
        """Test analytics action methods"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
        })
        
        # Test action_view_workflow
        result = analytics.action_view_workflow()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'motakamel.workflow')
        self.assertEqual(result['res_id'], workflow.id)
        
        # Test action_view_stage
        if analytics.stage_id:
            result = analytics.action_view_stage()
            self.assertEqual(result['type'], 'ir.actions.act_window')
            self.assertEqual(result['res_model'], 'motakamel.workflow.stage')
            self.assertEqual(result['res_id'], analytics.stage_id.id)

    def test_analytics_validation(self):
        """Test analytics validation rules"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        # Test valid analytics
        analytics = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'record_count': 100,
            'avg_duration': 24.5,
        })
        self.assertTrue(analytics.id)
        
        # Test negative values (should be allowed)
        analytics2 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'record_count': -10,
            'avg_duration': -5.0,
        })
        self.assertTrue(analytics2.id)

    def test_analytics_aggregation(self):
        """Test analytics aggregation methods"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
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
        
        # Create multiple analytics records
        analytics1 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage1.id,
            'record_count': 100,
            'avg_duration': 10.0,
        })
        
        analytics2 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage2.id,
            'record_count': 50,
            'avg_duration': 20.0,
        })
        
        # Test workflow-level aggregation
        workflow_analytics = self.WorkflowAnalytics.search([('workflow_id', '=', workflow.id)])
        total_records = sum(a.record_count for a in workflow_analytics)
        avg_duration = sum(a.avg_duration for a in workflow_analytics) / len(workflow_analytics)
        
        self.assertEqual(total_records, 150)
        self.assertEqual(avg_duration, 15.0)

    def test_analytics_bottleneck_detection(self):
        """Test analytics bottleneck detection"""
        workflow = self.Workflow.create({
            'name': 'Test Workflow',
            'description': 'Test workflow',
        })
        
        stage1 = self.WorkflowStage.create({
            'name': 'Fast Stage',
            'workflow_id': workflow.id,
            'sequence': 10,
        })
        
        stage2 = self.WorkflowStage.create({
            'name': 'Slow Stage',
            'workflow_id': workflow.id,
            'sequence': 20,
        })
        
        # Create analytics with different durations
        analytics1 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage1.id,
            'record_count': 100,
            'avg_duration': 5.0,
        })
        
        analytics2 = self.WorkflowAnalytics.create({
            'workflow_id': workflow.id,
            'stage_id': stage2.id,
            'record_count': 100,
            'avg_duration': 50.0,
            'bottleneck_reason': 'Complex processing',
        })
        
        # Test bottleneck detection
        workflow_analytics = self.WorkflowAnalytics.search([('workflow_id', '=', workflow.id)])
        bottlenecks = workflow_analytics.filtered(lambda a: a.bottleneck_reason)
        
        self.assertEqual(len(bottlenecks), 1)
        self.assertEqual(bottlenecks[0], analytics2)
        self.assertEqual(bottlenecks[0].bottleneck_reason, 'Complex processing')
