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


class MotakamelWorkflowStage(models.Model):
    _name = 'motakamel.workflow.stage'
    _description = 'Motakamel Workflow Stage'
    _order = 'workflow_id, sequence'

    name = fields.Char(string='Stage Name', required=True)
    workflow_id = fields.Many2one('motakamel.workflow', string='Workflow', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    icon = fields.Char(string='Icon Path')
    color = fields.Char(string='Color', default='#95a5a6')
    button_label = fields.Char(string='Button Label', default='Open')
    action_method = fields.Char(string='Action Method', default='action_open_module')
    technical_name = fields.Char(string='Technical Name', help='Technical name of the module')
    menu_xmlid = fields.Char(string='Menu XML ID', help='XML ID of the menu to open')
    module_xml_ids = fields.Char(string='Module XML IDs', help='Comma-separated list of module XML IDs')
    action_xml_ids = fields.Char(string='Action XML IDs', help='Comma-separated list of action XML IDs')
    next_stage_ids = fields.Many2many('motakamel.workflow.stage', 'workflow_stage_transition_rel', 
                                    'from_stage_id', 'to_stage_id', string='Next Stages')
    required_fields = fields.Text(string='Required Fields', help='JSON string of required fields')
    active = fields.Boolean(string='Active', default=True)
    
    # Computed fields
    transition_count = fields.Integer(string='Transition Count', compute='_compute_transition_count')
    record_count = fields.Integer(string='Record Count', compute='_compute_record_count')
    
    @api.depends('next_stage_ids')
    def _compute_transition_count(self):
        for record in self:
            record.transition_count = len(record.next_stage_ids)
    
    @api.depends('workflow_id', 'workflow_id.analytics_ids')
    def _compute_record_count(self):
        for record in self:
            analytics = self.env['motakamel.workflow.analytics'].search([
                ('workflow_id', '=', record.workflow_id.id),
                ('stage_id', '=', record.id)
            ], limit=1)
            record.record_count = analytics.record_count if analytics else 0

    def action_open_stage_modules(self):
        """Open modules related to this stage"""
        self.ensure_one()
        if not self.module_xml_ids:
            return False
        
        # Try to find the first available module action
        module_ids = [x.strip() for x in self.module_xml_ids.split(',') if x.strip()]
        for module_xml_id in module_ids:
            try:
                action = self.env.ref(module_xml_id, raise_if_not_found=False)
                if action and hasattr(action, 'action') and action.action:
                    return action.action.read()[0]
            except:
                continue
        
        return False

    def action_open_stage_actions(self):
        """Open actions related to this stage"""
        self.ensure_one()
        if not self.action_xml_ids:
            return False
        
        # Try to find the first available action
        action_ids = [x.strip() for x in self.action_xml_ids.split(',') if x.strip()]
        for action_xml_id in action_ids:
            try:
                action = self.env.ref(action_xml_id, raise_if_not_found=False)
                if action:
                    return action.read()[0]
            except:
                continue
        
        return False

    def action_open_module(self):
        """Open the module menu specified by menu_xmlid"""
        self.ensure_one()
        if not self.menu_xmlid:
            return False
        
        try:
            menu = self.env.ref(self.menu_xmlid, raise_if_not_found=False)
            if menu and menu.action:
                return menu.action.read()[0]
        except Exception as e:
            # If menu not found, try to find a similar menu
            pass
        
        return False

    def action_transition_to_next(self):
        """Transition to the next stage"""
        self.ensure_one()
        if not self.next_stage_ids:
            return False
        
        # For now, just open the first next stage
        next_stage = self.next_stage_ids[0]
        return {
            'type': 'ir.actions.act_window',
            'name': f'Transition to {next_stage.name}',
            'res_model': 'motakamel.workflow.stage',
            'res_id': next_stage.id,
            'view_mode': 'form',
            'target': 'current',
        }
