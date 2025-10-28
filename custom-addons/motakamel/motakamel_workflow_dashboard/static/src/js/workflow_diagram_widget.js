odoo.define('motakamel_workflow_dashboard.WorkflowDiagramWidget', function (require) {
    'use strict';

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var _t = core._t;

    var WorkflowDiagramWidget = AbstractField.extend({
        className: 'o_workflow_diagram_widget',
        supportedFieldTypes: ['char'],

        init: function () {
            this._super.apply(this, arguments);
            this.workflowData = null;
        },

        willStart: function () {
            return this._super.apply(this, arguments);
        },

        start: function () {
            this._super.apply(this, arguments);
            this._renderDiagram();
        },

        _renderDiagram: function () {
            var self = this;
            
            // Create SVG container
            var svg = d3.select(this.el)
                .append('svg')
                .attr('width', '100%')
                .attr('height', '400')
                .attr('viewBox', '0 0 800 400');

            // Sample workflow data (in real implementation, this would come from the field)
            var workflowData = {
                name: 'Student Lifecycle',
                stages: [
                    { id: 1, name: 'Inquiry', x: 100, y: 200, color: '#e74c3c' },
                    { id: 2, name: 'Admission', x: 250, y: 200, color: '#f39c12' },
                    { id: 3, name: 'Registration', x: 400, y: 200, color: '#2ecc71' },
                    { id: 4, name: 'Enrollment', x: 550, y: 200, color: '#9b59b6' },
                    { id: 5, name: 'Academic Progress', x: 700, y: 200, color: '#1abc9c' }
                ],
                transitions: [
                    { from: 1, to: 2 },
                    { from: 2, to: 3 },
                    { from: 3, to: 4 },
                    { from: 4, to: 5 }
                ]
            };

            // Draw workflow diagram
            this._drawWorkflowDiagram(svg, workflowData);
        },

        _drawWorkflowDiagram: function (svg, data) {
            var self = this;

            // Draw transitions (arrows)
            svg.selectAll('.transition')
                .data(data.transitions)
                .enter()
                .append('line')
                .attr('class', 'transition')
                .attr('x1', function (d) {
                    var fromStage = data.stages.find(s => s.id === d.from);
                    return fromStage ? fromStage.x + 60 : 0;
                })
                .attr('y1', function (d) {
                    var fromStage = data.stages.find(s => s.id === d.from);
                    return fromStage ? fromStage.y : 0;
                })
                .attr('x2', function (d) {
                    var toStage = data.stages.find(s => s.id === d.to);
                    return toStage ? toStage.x - 10 : 0;
                })
                .attr('y2', function (d) {
                    var toStage = data.stages.find(s => s.id === d.to);
                    return toStage ? toStage.y : 0;
                })
                .attr('stroke', '#666')
                .attr('stroke-width', 2)
                .attr('marker-end', 'url(#arrowhead)');

            // Add arrow marker
            svg.append('defs')
                .append('marker')
                .attr('id', 'arrowhead')
                .attr('markerWidth', 10)
                .attr('markerHeight', 7)
                .attr('refX', 9)
                .attr('refY', 3.5)
                .attr('orient', 'auto')
                .append('polygon')
                .attr('points', '0 0, 10 3.5, 0 7')
                .attr('fill', '#666');

            // Draw stages (circles)
            var stages = svg.selectAll('.stage')
                .data(data.stages)
                .enter()
                .append('g')
                .attr('class', 'stage')
                .attr('transform', function (d) {
                    return 'translate(' + d.x + ',' + d.y + ')';
                });

            stages.append('circle')
                .attr('r', 30)
                .attr('fill', function (d) { return d.color; })
                .attr('stroke', '#fff')
                .attr('stroke-width', 3)
                .style('cursor', 'pointer')
                .on('click', function (d) {
                    self._onStageClick(d);
                });

            stages.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .attr('fill', '#fff')
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .text(function (d) { return d.name; });

            // Add workflow title
            svg.append('text')
                .attr('x', 400)
                .attr('y', 50)
                .attr('text-anchor', 'middle')
                .attr('font-size', '20px')
                .attr('font-weight', 'bold')
                .attr('fill', '#333')
                .text(data.name);
        },

        _onStageClick: function (stage) {
            // Handle stage click - in real implementation, this would navigate to the stage
            console.log('Clicked stage:', stage.name);
            
            // Show notification
            this.do_notify(_t('Stage Clicked'), _t('You clicked on: ') + stage.name);
        },

        _setValue: function (value) {
            this._super.apply(this, arguments);
            // Handle value changes if needed
        }
    });

    core.form_widget_registry.add('workflow_diagram', WorkflowDiagramWidget);

    return WorkflowDiagramWidget;
});
