# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaterialRequest(models.Model):
    _name = 'material.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Material Request'

    name = fields.Char(string="", tracking=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id,
                                 tracking=True)
    request_date = fields.Date(string="Request Date", default=fields.Date.context_today, tracking=True)
    # project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=True, tracking=True)
    # analytic_account_id = fields.Many2one(string="Analytic Account", related="project_id.analytic_account_id", tracking=True)
    picking_type_id = fields.Many2one(comodel_name="stock.picking.type", string="Picking Type", required=False,
                                      tracking=True)
    location_destination_id = fields.Many2one(comodel_name="stock.location", string="Destination Location",
                                              required=False, tracking=True)
    location_src_id = fields.Many2one(comodel_name="stock.location", string="Source Location", required=False,
                                      tracking=True)
    state = fields.Selection(string="",
                             selection=[('draft', 'Draft'), ('confirm', 'Confirmed'),
                                        ('cancel', 'Canceled'), ],
                             default="draft", tracking=True, copy=False)
    # state = fields.Selection(string="",
    #                          selection=[('draft', 'Draft'), ('PR_Sent', 'PR Sent'),
    #                                     ('leader_approved', 'Approved'),
    #                                     ('CFO_Approved', 'CFO Approved'), ('confirm', 'Confirmed'),
    #                                     ('cancel', 'Canceled'), ],
    #                          default="draft", tracking=True, copy=False)
    request_line_ids = fields.One2many(comodel_name="material.request.line", inverse_name="request_id", tracking=True)
    picking_ids = fields.Many2many(comodel_name="stock.picking", string="picking", required=False, tracking=True,
                                   copy=False)
    # pr_ids = fields.Many2many(comodel_name="purchase.requests", string="PR", required=False, tracking=True,
    #
    #                           copy=False)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('material.request')
        return super(MaterialRequest, self).create(vals)

    # def create_purchase_request_pr(self):
    #     for rec in self:
    #         liens = rec.request_line_ids.filtered(lambda l: not l.is_available)
    #         if liens:
    #             pr = self.env['purchase.requests'].create({
    #                 'description': rec.name,
    #                 'start_date': fields.Date.today(),
    #             })
    #             liens.create_pr_line(pr)
    #             rec.pr_ids = [(4, pr.id)]

    def create_picking(self):
        for rec in self:
            # rec.create_purchase_request_pr()
            liens = rec.request_line_ids.filtered(lambda l: l.is_available)
            locations = set(liens.mapped('location_src_id'))
            for location in locations:
                picking = self.env['stock.picking'].create({
                    'picking_type_id': rec.picking_type_id.id,
                    'location_id': location.id,
                    'location_dest_id': rec.location_destination_id.id,
                    'origin': rec.name,
                })
                liens.filtered(lambda l: l.location_src_id == location).create_stock_move(picking)
                picking.action_confirm()
                rec.picking_ids = [(4, picking.id)]

    def open_picking(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock picking',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('origin', '=', self.name)],
        }

    # def open_pr(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'purchase requests',
    #         'res_model': 'purchase.requests',
    #         'view_mode': 'list,form',
    #         'domain': [('id', 'in', self.pr_ids.ids)],
    #     }

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            rec.create_picking()

    # def action_CFO_Approved(self):
    #     for rec in self:
    #         rec.state = 'CFO_Approved'

    # def action_leader_approved(self):
    #     for rec in self:
    #         rec.state = 'leader_approved'

    # def action_PR_Sent(self):
    #     for rec in self:
    #         rec.state = 'PR_Sent'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.picking_ids.action_cancel()

    @api.onchange('picking_type_id')
    def get_location(self):
        for rec in self:
            rec.update({'location_destination_id': rec.picking_type_id.default_location_dest_id.id,
                        'location_src_id': rec.picking_type_id.default_location_src_id.id})


class MaterialRequestLine(models.Model):
    _name = 'material.request.line'
    _description = 'Material Request Line'

    request_id = fields.Many2one(comodel_name="material.request", string="Request", required=False, )
    # purchase_request_line_id = fields.Many2one(comodel_name="purchase.request.line")
    stock_move_id = fields.Many2one(comodel_name="stock.move")
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=True, )
    name = fields.Char(string="Description", required=True, )
    # task_id = fields.Many2one('project.task', string="Cost sheet", required=True)
    quantity = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="get_subtotal")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", compute="get_uom_id", store=True, readonly=False)
    state = fields.Selection(related="request_id.state", store=True)
    location_src_id = fields.Many2one(comodel_name="stock.location", string="Source Location")
    is_available = fields.Boolean(string="Available", default=True)

    # @api.onchange('product_id', 'quantity')
    # @api.constrains('product_id', 'quantity')
    # def get_location(self):
    #     for rec in self:
    #         stock_quant = self.env['stock.quant'].sudo().search(
    #             [('product_id', '=', rec.product_id.id), ('quantity', '>=', rec.quantity)], limit=1)
    #         rec.location_src_id = stock_quant.location_id.id if stock_quant else False
    #         rec.is_available = True if stock_quant else False

    @api.depends('quantity', 'price_unit')
    def get_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit

    @api.depends('product_id')
    def get_uom_id(self):
        for rec in self:
            rec.uom_id = rec.product_id.uom_id.id
            rec.name = rec.product_id.name

    def create_stock_move(self, picking):
        for rec in self:
            rec.stock_move_id = self.env['stock.move'].create({
                'name': rec.product_id.display_name or rec.product_id.name,
                'product_id': rec.product_id.id,
                'product_uom_qty': rec.quantity,
                'product_uom': rec.uom_id.id,
                'picking_id': picking.id,
                'picking_type_id': picking.picking_type_id.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            }).id

    # def create_stock_move(self, picking):
    #     for rec in self:
    #         if rec.product_id.id == 'product':
    #             rec.stock_move_id = self.env['stock.move'].create({
    #                 'name': rec.product_id.name,
    #                 'product_id': rec.product_id.id,
    #                 'product_uom_qty': rec.quantity,
    #                 'product_uom': rec.uom_id.id,
    #                 'picking_id': picking.id,
    #                 'picking_type_id': picking.picking_type_id.id,
    #                 'location_id': picking.location_id.id,
    #                 'location_dest_id': picking.location_dest_id.id,
    #             }).id

    def create_pr_line(self, pr):
        for rec in self:
            rec.purchase_request_line_id = self.env['purchase.request.line'].create({
                'name': rec.product_id.name,
                'product_id': rec.product_id.id,
                'product_qty': rec.quantity,
                'request_line_id': pr.id,
            }).id
