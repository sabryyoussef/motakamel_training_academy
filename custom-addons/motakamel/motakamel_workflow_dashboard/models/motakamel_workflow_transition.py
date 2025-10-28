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


class MotakamelWorkflowTransition(models.Model):
    _name = 'motakamel.workflow.transition'
    _description = 'Motakamel Workflow Transition'
    _order = 'workflow_id, sequence'

    name = fields.Char(string='Transition Name', required=True)
    workflow_id = fields.Many2one('motakamel.workflow', string='Workflow', required=True, ondelete='cascade')
    from_stage_id = fields.Many2one('motakamel.workflow.stage', string='From Stage', required=True)
    to_stage_id = fields.Many2one('motakamel.workflow.stage', string='To Stage', required=True)
    button_label = fields.Char(string='Button Label', required=True)
    condition = fields.Text(string='Condition', help='Python expression for conditional transitions')
    action_xml_id = fields.Char(string='Action XML ID', help='Action to execute on transition')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Computed fields
    transition_type = fields.Selection([
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('conditional', 'Conditional'),
    ], string='Transition Type', compute='_compute_transition_type')
    
    @api.depends('condition')
    def _compute_transition_type(self):
        for record in self:
            if record.condition:
                record.transition_type = 'conditional'
            elif record.action_xml_id:
                record.transition_type = 'manual'
            else:
                record.transition_type = 'automatic'

    def action_execute_transition(self):
        """Execute the transition"""
        self.ensure_one()
        
        # Check condition if exists
        if self.condition:
            try:
                # Simple condition evaluation (can be enhanced)
                if not eval(self.condition):
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Transition Blocked',
                            'message': 'Transition condition not met.',
                            'type': 'warning',
                        }
                    }
            except:
                pass
        
        # Execute action if exists
        if self.action_xml_id:
            try:
                action = self.env.ref(self.action_xml_id, raise_if_not_found=False)
                if action:
                    return action.read()[0]
            except:
                pass
        
        # Default: navigate to target stage
        return {
            'type': 'ir.actions.act_window',
            'name': f'Transition to {self.to_stage_id.name}',
            'res_model': 'motakamel.workflow.stage',
            'res_id': self.to_stage_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.constrains('from_stage_id', 'to_stage_id')
    def _check_stages_same_workflow(self):
        """Ensure both stages belong to the same workflow"""
        for record in self:
            if record.from_stage_id.workflow_id != record.to_stage_id.workflow_id:
                raise ValidationError("Both stages must belong to the same workflow.")
