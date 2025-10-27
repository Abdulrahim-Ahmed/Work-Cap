# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OperationName(models.Model):
    _inherit = 'mrp.workorder'

    name_new_opp = fields.Many2one('mrp.operation.name', string="Operation Name")
    name = fields.Char(string='Operation Old', required=True)

    @api.onchange('name_new_opp')
    def onchange_name_new_opp(self):
        if self.name_new_opp:
            # Access the first record in the recordset
            self.name = self.name_new_opp.name_new_opp
        else:
            self.name = ''

    @api.onchange('name')
    def onchange_name(self):
        """Update or create 'name_new_opp' based on 'name' field value."""
        if self.name:
            operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', self.name)], limit=1)
            if operation:
                self.name_new_opp = operation
            else:
                new_operation = self.env['mrp.operation.name'].create({
                    'name_new_opp': self.name,
                    'name': self.name
                })
                self.name_new_opp = new_operation
        else:
            self.name_new_opp = False

    @api.model
    def default_get(self, fields):
        """Automatically fill fields when a new record is initialized."""
        res = super(OperationName, self).default_get(fields)
        if 'name' in res and res['name']:
            # Try to find the matching operation and set name_new_opp
            operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', res['name'])], limit=1)
            if operation:
                res['name_new_opp'] = operation.id
        return res
    # --------------------
    # @api.onchange('name')
    # def onchange_name(self):
    #     if self.name:
    #         # Check if there's an operation with this name
    #         operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', self.name)], limit=1)
    #         if operation:
    #             # If found, set the name_new_opp field
    #             self.name_new_opp = operation
    #         else:
    #             # If no operation is found, create a new record with the name value
    #             new_operation = self.env['mrp.operation.name'].create({'name_new_opp': self.name, 'name': self.name})
    #             self.name_new_opp = new_operation
    #     else:
    #         self.name_new_opp = False
    #
    # @api.model
    # def default_get(self, fields):
    #     """Automatically fill in fields when a new record is initialized."""
    #     res = super(OperationName, self).default_get(fields)
    #     if 'name' in res and res['name']:
    #         operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', res['name'])], limit=1)
    #         if operation:
    #             res['name_new_opp'] = operation.id
    #     return res
    # ----------------
    # @api.model
    # def create(self, vals):
    #     if 'name_new_opp' in vals and vals['name_new_opp']:
    #         operation = self.env['mrp.operation.name'].browse(vals['name_new_opp'])
    #         vals['name'] = operation.name_new_opp
    #     return super(OperationName, self).create(vals)
    # --------------------------
    # @api.model
    # def create(self, vals):
    #     # Sync name and name_new_opp during record creation
    #     if 'name_new_opp' in vals and vals['name_new_opp']:
    #         operation = self.env['mrp.operation.name'].browse(vals['name_new_opp'])
    #         vals['name'] = operation.name_new_opp
    #
    #     if 'name' in vals and vals['name']:
    #         operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', vals['name'])], limit=1)
    #         if not operation:
    #             operation = self.env['mrp.operation.name'].create({'name_new_opp': vals['name'], 'name': vals['name']})
    #         vals['name_new_opp'] = operation.id
    #
    #     return super(OperationName, self).create(vals)
    #
    # def write(self, vals):
    #     # Sync name and name_new_opp during record update
    #     if 'name_new_opp' in vals and vals['name_new_opp']:
    #         operation = self.env['mrp.operation.name'].browse(vals['name_new_opp'])
    #         vals['name'] = operation.name_new_opp
    #
    #     if 'name' in vals and vals['name']:
    #         operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', vals['name'])], limit=1)
    #         if not operation:
    #             operation = self.env['mrp.operation.name'].create({'name_new_opp': vals['name'], 'name': vals['name']})
    #         vals['name_new_opp'] = operation.id
    #
    #     return super(OperationName, self).write(vals)

    # ----------------------------
    @api.model
    def create(self, vals):
        """Automatically copy the value from name to name_new_opp upon creation."""
        if 'name' in vals and vals['name']:
            # Check if an operation with the same name exists
            operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', vals['name'])], limit=1)
            if operation:
                # If found, set the name_new_opp to the existing operation
                vals['name_new_opp'] = operation.id
            else:
                # If no matching operation exists, create a new one
                new_operation = self.env['mrp.operation.name'].create({
                    'name_new_opp': vals['name'],
                    'name': vals['name']
                })
                vals['name_new_opp'] = new_operation.id  # Set the ID of the new operation

        # Call the super method to create the record
        return super(OperationName, self).create(vals)

    def write(self, vals):
        """Sync name and name_new_opp during updates."""
        if 'name_new_opp' in vals and vals['name_new_opp']:
            operation = self.env['mrp.operation.name'].browse(vals['name_new_opp'])
            vals['name'] = operation.name_new_opp

        if 'name' in vals and vals['name']:
            operation = self.env['mrp.operation.name'].search([('name_new_opp', '=', vals['name'])], limit=1)
            if not operation:
                operation = self.env['mrp.operation.name'].create({
                    'name_new_opp': vals['name'],
                    'name': vals['name']
                })
            vals['name_new_opp'] = operation.id

        return super(OperationName, self).write(vals)

    # @api.onchange('name_new_opp')
    # def _onchange_name_new_opp(self):
    #     if self.name_new_opp:
    #         self.name = self.name_new_opp.name
    #
    # @api.depends('name_new_opp')
    # def _compute_name(self):
    #     for record in self:
    #         if record.name_new_opp:
    #             record.name = record.name_new_opp.name
