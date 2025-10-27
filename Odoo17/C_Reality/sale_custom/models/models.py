from odoo import models, fields, api


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    height = fields.Integer(string="Height")
    length = fields.Integer(string="Length")
    width = fields.Integer(string="Width")
    image_2d = fields.Image()
    material_ids = fields.Many2many('product.material', 'product_material_product_template_rel', string='Material')
    color_ids = fields.Many2many('product.color', 'product_color_product_template_rel', string='Colors')
    fabric_ids = fields.Many2many('product.fabric', 'product_fabric_product_template_rel', string='Fabrics')
    glass_ids = fields.Many2many('product.glass', 'product_glass_product_template_rel', string='Glasses')
    metal_tag_ids = fields.Many2many('product.metal.tag', string='Metal')


class Product_custom_inherit(models.Model):
    _inherit = "product.product"

    height1 = fields.Integer(string="Height")
    length1 = fields.Integer(string="Length")
    width1 = fields.Integer(string="Width")


class EditSale(models.Model):
    _inherit = 'sale.order.line'

    image_p = fields.Image(related='product_id.image_1920')
    image_d = fields.Image(related='product_id.image_2d')
    edited_height = fields.Integer(string="H", readonly=False, store=True)
    edited_length = fields.Integer(string="L", readonly=False, store=True)
    edited_width = fields.Integer(string="W", readonly=False, store=True)
    edited_material_ids = fields.Many2many('product.material', readonly=False, store=True, string="Material")
    edited_color_ids = fields.Many2many('product.color', readonly=False, store=True, string="Colors")
    edited_metal_ids = fields.Many2many('product.metal.tag', readonly=False, store=True, string="Metals")
    edited_fabric_ids = fields.Many2many('product.fabric', readonly=False, store=True, string="Fabrics")
    edited_glass_ids = fields.Many2many('product.glass', readonly=False, store=True, string="Glasses")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # print("Running _onchange_product_id")
        if self.product_id:
            self.edited_height = self.product_id.height1
            self.edited_length = self.product_id.length1
            self.edited_width = self.product_id.width1
            self.edited_material_ids = [(6, 0, self.product_id.material_ids.ids)]
            self.edited_color_ids = [(6, 0, self.product_id.color_ids.ids)]
            self.edited_metal_ids = [(6, 0, self.product_id.metal_tag_ids.ids)]
            self.edited_fabric_ids = [(6, 0, self.product_id.fabric_ids.ids)]
            self.edited_glass_ids = [(6, 0, self.product_id.glass_ids.ids)]


class MrpProductionInheritSale(models.Model):
    _inherit = 'mrp.production'

    image_p = fields.Image(string="Image", related='product_id.image_1920')
    image_d = fields.Image(string="Image_2D", related='product_id.image_2d')
    sale_order_line_id = fields.Many2one('sale.order.line', compute='_compute_sale_order_line', store=True,
                                         string="Sale Order Line")
    height_mrp = fields.Integer(string="H", compute='_compute_values_from_sale_order_line', store=True)
    length_mrp = fields.Integer(string="L", compute='_compute_values_from_sale_order_line', store=True)
    width_mrp = fields.Integer(string="W", compute='_compute_values_from_sale_order_line', store=True)
    mrp_material_ids = fields.Many2many('product.material', compute='_compute_values_from_sale_order_line',
                                        store=True, string="Material")
    mrp_color_ids = fields.Many2many('product.color', compute='_compute_values_from_sale_order_line', store=True,
                                     string="Colors")
    mrp_metal_ids = fields.Many2many('product.metal.tag', compute='_compute_values_from_sale_order_line', store=True,
                                     string="Metals")
    mrp_fabric_ids = fields.Many2many('product.fabric', compute='_compute_values_from_sale_order_line', store=True,
                                      string="Fabrics")
    mrp_glass_ids = fields.Many2many('product.glass', compute='_compute_values_from_sale_order_line', store=True,
                                     string="Glasses")
    customer_sale_id = fields.Many2one('res.partner', string="Customer",
                                       related='sale_order_line_id.order_id.partner_id',
                                       store=True, readonly=True)
    tag_ids = fields.Many2many('mrp.production.tag', string='Tags')

    @api.depends('origin', 'product_id')
    def _compute_sale_order_line(self):
        for production in self:
            # Your extended search with the exclusion of already linked sale order lines
            sale_order_lines = self.env['sale.order.line'].search(
                [('order_id.name', '=', production.origin),
                 ('product_id', '=', production.product_id.id),
                 ('id', 'not in', self.mapped('sale_order_line_id').ids)],
                order='create_date desc')
            # Diagnostic prints
            print(
                f"Found {len(sale_order_lines)} sale order lines for MO {production.name}. Lines: {[line.id for line in sale_order_lines]}")

            # Link the MO to the first available sale order line
            production.sale_order_line_id = sale_order_lines and sale_order_lines[0] or False

    @api.depends('sale_order_line_id')
    def _compute_values_from_sale_order_line(self):
        print("Running _compute_values_from_sale_order_line")
        for production in self:
            sale_line = production.sale_order_line_id
            if sale_line:
                production.height_mrp = sale_line.edited_height
                production.length_mrp = sale_line.edited_length
                production.width_mrp = sale_line.edited_width
                production.mrp_material_ids = [(6, 0, sale_line.edited_material_ids.ids)]
                production.mrp_color_ids = [(6, 0, sale_line.edited_color_ids.ids)]
                production.mrp_metal_ids = [(6, 0, sale_line.edited_metal_ids.ids)]
                production.mrp_fabric_ids = [(6, 0, sale_line.edited_fabric_ids.ids)]
                production.mrp_glass_ids = [(6, 0, sale_line.edited_glass_ids.ids)]
                print(f"Updated fields for MO {production.name} from Sale Order Line {sale_line.id}")
