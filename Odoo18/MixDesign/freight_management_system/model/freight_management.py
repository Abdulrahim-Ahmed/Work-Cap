# -*- coding: utf-8 -*-

from odoo import models, fields, api


# from datetime import timedelta


class FreightCycle(models.Model):
    _name = 'freight.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Freight Management'

    name = fields.Char(string='Freight Name', required=True, tracking=True)
    # description = fields.Text(string='Description')
    date = fields.Datetime(
        string="Freight Date",
        required=True, copy=False, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    line_ids = fields.One2many('freight.management.line', 'freight_id', string='Lines')
    order_code = fields.Char(string='Freight Code', readonly=True, help="Code of the linked Freight Order")

    # def action_confirm(self):
    #     for record in self:
    #         # Find the project by the stored order code
    #         project = self.env['project.project'].search([('name', '=', record.order_code)], limit=1)
    #
    #         # Create tasks under the found project
    #         for line in record.line_ids:
    #             self.env['project.task'].create({
    #                 'name': line.name,
    #                 'project_id': project.id,
    #                 'user_ids': [(6, 0, [line.assignees.id])],
    #             })
    #         record.state = 'confirmed'

    # def action_confirm(self):
    #     for record in self:
    #         # Find the project by the stored order code
    #         project = self.env['project.project'].search([('name', '=', record.order_code)], limit=1)
    #
    #         if project and record.line_ids:
    #             # ✅ GET ALL STAGES USED IN THE LINES
    #             stages_used = record.line_ids.mapped('stage_id')
    #
    #             # ✅ LINK THESE STAGES TO THE PROJECT (if not already linked)
    #             for stage in stages_used:
    #                 if stage and project.id not in stage.project_ids.ids:
    #                     stage.project_ids = [(4, project.id)]  # Link stage to project
    #
    #             # ✅ CREATE TASKS AND ASSIGN TO THEIR SELECTED STAGES
    #             for line in record.line_ids:
    #                 self.env['project.task'].create({
    #                     'name': line.name,
    #                     'project_id': project.id,
    #                     'stage_id': line.stage_id.id if line.stage_id else False,
    #                     'user_ids': [(6, 0, [line.assignees.id])] if line.assignees else False,
    #                     # 'priority': getattr(line, 'priority', '0') or '0',
    #                     # 'description': getattr(line, 'description', '') or '',
    #                     # 'date_deadline': getattr(line, 'deadline', False) or False,
    #                 })
    #
    #         record.state = 'confirmed'

    def action_confirm(self):
        for record in self:
            # Find the project by the stored order code
            project = self.env['project.project'].search([('name', '=', record.order_code)], limit=1)

            if project and record.line_ids:

                # ✅ CREATE TASKS AND ASSIGN TO THEIR SELECTED STAGES
                for line in record.line_ids:
                    self.env['project.task'].create({
                        'name': line.name,
                        'project_id': project.id,
                        'stage_id': line.stage_id.id if line.stage_id else False,
                        'user_ids': [(6, 0, [line.assignees.id])] if line.assignees else False,
                    })

            record.state = 'confirmed'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_draft(self):
        for record in self:
            record.state = 'draft'
