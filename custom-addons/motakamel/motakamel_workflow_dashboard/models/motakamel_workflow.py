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
import json


class MotakamelWorkflow(models.Model):
    _name = 'motakamel.workflow'
    _description = 'Motakamel Workflow'
    _order = 'sequence, name'

    name = fields.Char(string='Workflow Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    icon = fields.Char(string='Icon Path')
    color = fields.Char(string='Color', default='#3498db')
    active = fields.Boolean(string='Active', default=True)
    stage_ids = fields.One2many('motakamel.workflow.stage', 'workflow_id', string='Stages')
    transition_ids = fields.One2many('motakamel.workflow.transition', 'workflow_id', string='Transitions')
    user_group_ids = fields.Many2many('res.groups', string='User Groups')
    analytics_ids = fields.One2many('motakamel.workflow.analytics', 'workflow_id', string='Analytics')
    
    # Computed fields
    stage_count = fields.Integer(string='Stage Count', compute='_compute_stage_count')
    progress_percentage = fields.Float(string='Progress %', compute='_compute_progress_percentage')
    
    @api.depends('stage_ids')
    def _compute_stage_count(self):
        for record in self:
            record.stage_count = len(record.stage_ids)
    
    @api.depends('analytics_ids')
    def _compute_progress_percentage(self):
        for record in self:
            if record.analytics_ids:
                total_records = sum(analytics.record_count for analytics in record.analytics_ids)
                completed_records = sum(analytics.record_count for analytics in record.analytics_ids if analytics.stage_id.sequence == record.stage_count)
                record.progress_percentage = (completed_records / total_records * 100) if total_records > 0 else 0
            else:
                record.progress_percentage = 0

    def action_open_workflow_dashboard(self):
        """Open the workflow-specific dashboard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Dashboard',
            'res_model': 'motakamel.workflow',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('motakamel_workflow_dashboard.view_workflow_dashboard_form').id,
            'target': 'current',
            'context': {'workflow_id': self.id},
        }

    def action_view_stages(self):
        """View all stages in this workflow"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Stages',
            'res_model': 'motakamel.workflow.stage',
            'view_mode': 'kanban,tree,form',
            'domain': [('workflow_id', '=', self.id)],
            'context': {'default_workflow_id': self.id},
        }

    def action_view_analytics(self):
        """View workflow analytics"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Analytics',
            'res_model': 'motakamel.workflow.analytics',
            'view_mode': 'tree,form',
            'domain': [('workflow_id', '=', self.id)],
            'context': {'default_workflow_id': self.id},
        }
