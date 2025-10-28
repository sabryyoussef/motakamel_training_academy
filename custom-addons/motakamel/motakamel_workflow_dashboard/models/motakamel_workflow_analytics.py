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
from datetime import datetime, timedelta


class MotakamelWorkflowAnalytics(models.Model):
    _name = 'motakamel.workflow.analytics'
    _description = 'Motakamel Workflow Analytics'
    _order = 'workflow_id, stage_id'

    workflow_id = fields.Many2one('motakamel.workflow', string='Workflow', required=True, ondelete='cascade')
    stage_id = fields.Many2one('motakamel.workflow.stage', string='Stage', required=True, ondelete='cascade')
    record_count = fields.Integer(string='Record Count', default=0)
    avg_duration = fields.Float(string='Average Duration (hours)', default=0.0)
    bottlenecks = fields.Text(string='Bottlenecks')
    last_updated = fields.Datetime(string='Last Updated', default=fields.Datetime.now)
    
    # Computed fields
    efficiency_score = fields.Float(string='Efficiency Score', compute='_compute_efficiency_score')
    trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], string='Trend', compute='_compute_trend')
    
    @api.depends('record_count', 'avg_duration')
    def _compute_efficiency_score(self):
        for record in self:
            if record.record_count > 0 and record.avg_duration > 0:
                # Simple efficiency calculation (can be enhanced)
                record.efficiency_score = min(100, max(0, 100 - (record.avg_duration * 10)))
            else:
                record.efficiency_score = 0
    
    @api.depends('last_updated', 'record_count')
    def _compute_trend(self):
        for record in self:
            # Simple trend calculation based on recent activity
            if record.last_updated:
                days_since_update = (datetime.now() - record.last_updated).days
                if days_since_update < 1:
                    record.trend = 'improving'
                elif days_since_update < 7:
                    record.trend = 'stable'
                else:
                    record.trend = 'declining'
            else:
                record.trend = 'stable'

    def action_refresh_analytics(self):
        """Refresh analytics data"""
        self.ensure_one()
        # This would typically query actual data from related models
        # For now, we'll simulate some data
        self.record_count = self.env['op.student'].search_count([]) if hasattr(self.env, 'op.student') else 0
        self.avg_duration = 24.0  # Simulated average duration
        self.last_updated = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Analytics Updated',
                'message': f'Analytics refreshed for {self.stage_id.name}',
                'type': 'success',
            }
        }

    def action_view_records(self):
        """View records in this stage"""
        self.ensure_one()
        # This would open the relevant model based on the stage
        # For now, we'll open a generic view
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.stage_id.name} Records',
            'res_model': 'op.student' if hasattr(self.env, 'op.student') else 'res.partner',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    @api.model
    def update_all_analytics(self):
        """Update analytics for all workflows"""
        workflows = self.env['motakamel.workflow'].search([])
        for workflow in workflows:
            for stage in workflow.stage_ids:
                analytics = self.search([
                    ('workflow_id', '=', workflow.id),
                    ('stage_id', '=', stage.id)
                ], limit=1)
                
                if not analytics:
                    analytics = self.create({
                        'workflow_id': workflow.id,
                        'stage_id': stage.id,
                    })
                
                analytics.action_refresh_analytics()
        
        return True
