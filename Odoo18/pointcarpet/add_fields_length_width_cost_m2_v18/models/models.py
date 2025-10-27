# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from collections import defaultdict
import re
import logging

_logger = logging.getLogger(__name__)


class StockValuationLayerCost(models.Model):
    _inherit = "stock.valuation.layer"

    area = fields.Float(string="Area (m²)", related="product_id.area", store=True)
    total_cost = fields.Float(string="Quantity (m²)", compute="_compute_total_area", store=True)
    value_per_total_cost = fields.Float(string="(m²) Value", compute="_compute_value_per_total_cost", store=True)

    @api.depends('area', 'quantity')
    def _compute_total_area(self):
        for record in self:
            record.total_cost = (record.area or 0.0) * (record.quantity or 0.0)

    @api.depends('value', 'total_cost')
    def _compute_value_per_total_cost(self):
        for record in self:
            if record.total_cost:
                record.value_per_total_cost = record.value / record.total_cost
            else:
                record.value_per_total_cost = 0.0


class StockQuantCost(models.Model):
    _inherit = "stock.quant"

    area = fields.Float(string="Area (m²)", related="product_id.area", store=True)
    total_cost = fields.Float(string="Total Cost (m²)", compute="_compute_total_area", store=True)

    @api.depends('area', 'inventory_quantity_auto_apply')
    def _compute_total_area(self):
        for record in self:
            record.total_cost = (record.area or 0.0) * (record.inventory_quantity_auto_apply or 0.0)


class AddFieldsLengthWidthCostM2Product(models.Model):
    _inherit = 'product.template'

    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    area = fields.Float(string="Area (m²)", compute="_compute_area", store=True)
    price_per_meter = fields.Float(string="Price Per Meter (m²)")
    cost_per_meter = fields.Float(string="Cost Per Meter (m²)")
    
    # Auto-calculate sales price as length * width * price_per_meter
    list_price = fields.Float(
        string='Sales Price',
        compute='_compute_list_price',
        store=True
    )

    @api.depends('length', 'width')
    def _compute_area(self):
        for product in self:
            product.area = (product.length or 0.0) * (product.width or 0.0)

    @api.depends('length', 'width', 'price_per_meter')
    def _compute_list_price(self):
        """Automatically calculate template sales price as length * width * price_per_meter"""
        for product in self:
            length = product.length or 0.0
            width = product.width or 0.0
            price_per_meter = product.price_per_meter or 0.0
            product.list_price = length * width * price_per_meter

    

    def action_parse_all_variants_size(self):
        """Parse size attributes for all variants of this template"""
        for variant in self.product_variant_ids:
            variant._parse_size_from_attributes()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Size attributes parsed for {len(self.product_variant_ids)} variants.',
                'type': 'success',
            }
        }


class AddFieldsLengthWidthCostM2Variants(models.Model):
    _inherit = 'product.product'

    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    area = fields.Float(string="Area (m²)", compute="_compute_area", store=True)
    cost_per_meter = fields.Float(string="Cost Per Meter (m²)")
    
    price_per_meter = fields.Float(
        related='product_tmpl_id.price_per_meter',
        string='Price Per Meter (m²)',
        readonly=False,
        store=True
    )
    
    # Auto-calculate sales price as length * width * price_per_meter
    lst_price = fields.Float(
        string='Sales Price',
        compute='_compute_lst_price',
        store=True
    )

    @api.depends('length', 'width')
    def _compute_area(self):
        for product in self:
            product.area = (product.length or 0.0) * (product.width or 0.0)

    

    @api.depends('length', 'width', 'price_per_meter')
    def _compute_lst_price(self):
        """Automatically calculate sales price as length * width * price_per_meter"""
        for product in self:
            length = product.length or 0.0
            width = product.width or 0.0
            price_per_meter = product.price_per_meter or 0.0
            product.lst_price = length * width * price_per_meter

    @api.model
    def create(self, vals):
        result = super(AddFieldsLengthWidthCostM2Variants, self).create(vals)
        result._parse_size_from_attributes()
        return result

    def write(self, vals):
        result = super(AddFieldsLengthWidthCostM2Variants, self).write(vals)
        # Parse size when attributes change or when manually triggered
        if any(field in vals for field in ['product_template_attribute_value_ids', 'attribute_value_ids', 'name']):
            self._parse_size_from_attributes()
        return result

    @api.onchange('product_template_attribute_value_ids')
    def _onchange_attributes(self):
        """Trigger size parsing when attributes change in the UI"""
        self._parse_size_from_attributes()

    def action_parse_size_manually(self):
        """Manual action to parse size from attributes - useful for existing products"""
        self._parse_size_from_attributes()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Size attributes have been parsed and length/width updated.',
                'type': 'success',
            }
        }

    def _parse_size_from_attributes(self):
        for product in self:
            size_attribute = None

            # Check product_template_attribute_value_ids first
            for attribute_value in product.product_template_attribute_value_ids:
                attr_name = attribute_value.attribute_id.name.lower()
                if 'size' in attr_name:
                    size_attribute = attribute_value.product_attribute_value_id.name
                    break

            # Check attribute_value_ids if not found
            if not size_attribute:
                for attribute_value in product.attribute_value_ids:
                    attr_name = attribute_value.attribute_id.name.lower()
                    if 'size' in attr_name:
                        size_attribute = attribute_value.name
                        break

            # Check product_variant_attribute_value_ids as additional fallback
            if not size_attribute:
                for attribute_value in product.product_template_attribute_value_ids.mapped(
                        'product_attribute_value_id'):
                    attr_name = attribute_value.attribute_id.name.lower()
                    if 'size' in attr_name and product.product_template_attribute_value_ids.filtered(
                            lambda x: x.product_attribute_value_id == attribute_value):
                        size_attribute = attribute_value.name
                        break

            if size_attribute:
                size_clean = size_attribute.replace('x', '*').replace('X', '*').strip()

                if '*' in size_clean:
                    try:
                        parts = size_clean.split('*')
                        if len(parts) >= 2:
                            # Get first two numeric parts
                            length_str = parts[0].strip()
                            width_str = parts[1].strip()

                            # Extract numeric values (handle cases like "1.5m", "2cm", etc.)
                            length_match = re.search(r'(\d+(?:\.\d+)?)', length_str)
                            width_match = re.search(r'(\d+(?:\.\d+)?)', width_str)

                            if length_match and width_match:
                                length_val = float(length_match.group(1))
                                width_val = float(width_match.group(1))

                                _logger.info(
                                    f"Product {product.name}: Parsed size '{size_attribute}' -> Length: {length_val}, Width: {width_val}")

                                # Only update if values are different to avoid unnecessary writes
                                if product.length != length_val or product.width != width_val:
                                    product.write({
                                        'length': length_val,
                                        'width': width_val
                                    })
                            else:
                                _logger.warning(
                                    f"Product {product.name}: Could not extract numeric values from size '{size_attribute}'")
                    except (ValueError, IndexError, AttributeError) as e:
                        _logger.error(f"Product {product.name}: Error parsing size attribute '{size_attribute}': {e}")
                        pass
                else:
                    _logger.debug(
                        f"Product {product.name}: Size attribute '{size_attribute}' does not contain '*' or 'x'")


class AddFieldsAtPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    cost_per_meter = fields.Float(string="Cost m2", related='product_id.cost_per_meter')

    # the below div to make the calculation
    @api.depends('product_id', 'product_qty', 'cost_per_meter', 'product_id.length', 'product_id.width',
                 'product_id.product_tmpl_id.length', 'product_id.product_tmpl_id.width')
    def _compute_price_unit(self):
        """
        Compute price_unit based on length, width, and cost_per_meter.
        Fallback to product.template if product.product fields are not available.
        """
        for line in self:
            if line.product_id and line.cost_per_meter:
                # Fetch length and width from product.product
                length = line.product_id.length
                width = line.product_id.width

                # If not defined in product.product, fallback to product.template
                if not length or not width:
                    length = line.product_id.product_tmpl_id.length
                    width = line.product_id.product_tmpl_id.width

                # Calculate price_unit if all values are present
                if length and width and line.cost_per_meter:
                    line.price_unit = length * width * line.cost_per_meter
                else:
                    # If any value is missing, keep the default price_unit
                    line.price_unit = line.price_unit or 0.0

    price_unit = fields.Float(compute="_compute_price_unit", store=True)

    def write(self, vals):
        """
        Override write method to update cost_per_meter in product and variant
        when it's changed in purchase order line
        """
        result = super(AddFieldsAtPurchaseOrderLine, self).write(vals)

        if 'cost_per_meter' in vals:
            for line in self:
                if line.product_id:
                    # Update cost_per_meter in product variant
                    line.product_id.write({'cost_per_meter': vals['cost_per_meter']})

                    # Update cost_per_meter in product template
                    line.product_id.product_tmpl_id.write({'cost_per_meter': vals['cost_per_meter']})

        return result

    @api.model
    def create(self, vals):
        """
        Override create method to update cost_per_meter in product and variant
        when purchase order line is created with cost_per_meter value
        """
        result = super(AddFieldsAtPurchaseOrderLine, self).create(vals)

        if 'cost_per_meter' in vals and vals['cost_per_meter'] and result.product_id:
            # Update cost_per_meter in product variant
            result.product_id.write({'cost_per_meter': vals['cost_per_meter']})

            # Update cost_per_meter in product template
            result.product_id.product_tmpl_id.write({'cost_per_meter': vals['cost_per_meter']})

        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def _compute_price_unit(self):
        """
        Sets price_unit based on whether the product is a variant or a template:
        - If it's a product variant (`product.product`), use `lst_price`.
        - If it's a template (`product.template`), use `list_price`.
        """
        for line in self:
            if line.product_id:
                if line.product_id.product_tmpl_id == line.product_id:
                    # It's a template (no variant selected)
                    line.price_unit = line.product_id.product_tmpl_id.list_price
                else:
                    # It's a variant
                    line.price_unit = line.product_id.lst_price

    price_unit = fields.Float(compute="_compute_price_unit", store=True)


class StockMoveAreaDemand(models.Model):
    _inherit = 'stock.move'

    length = fields.Float(string="Length", related='product_id.length', store=True)
    width = fields.Float(string="Width", related='product_id.width', store=True)
    total_area_demand = fields.Float(
        string="Quantity of m²",
        compute="_compute_total_area_demand",
        store=True,
        help="Length × Width × Demand quantity"
    )

    @api.depends('length', 'width', 'product_uom_qty')
    def _compute_total_area_demand(self):
        for move in self:
            area = (move.length or 0.0) * (move.width or 0.0)
            move.total_area_demand = area * (move.product_uom_qty or 0.0)


SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
    ('by_m2', 'By M²'),
]


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        self.ensure_one()
        lines = []

        for move in self._get_targeted_move_ids():
            if move.product_id.cost_method not in ('fifo', 'average') or move.state == 'cancel' or not move.quantity:
                continue
            qty = move.product_uom._compute_quantity(move.quantity, move.product_id.uom_id)

            # Calculate m² based on product dimensions
            length = getattr(move.product_id, 'length', 0.0) or 0.0
            width = getattr(move.product_id, 'width', 0.0) or 0.0

            # Fallback to template if variant doesn't have dimensions
            if not length or not width:
                length = getattr(move.product_id.product_tmpl_id, 'length', 0.0) or 0.0
                width = getattr(move.product_id.product_tmpl_id, 'width', 0.0) or 0.0

            m2_per_unit = length * width
            total_m2 = m2_per_unit * qty

            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': qty,
                'former_cost': sum(move._get_stock_valuation_layer_ids().mapped('value')),
                'weight': move.product_id.weight * qty,
                'volume': move.product_id.volume * qty,
                'm2': total_m2,
            }
            lines.append(vals)

        if not lines:
            target_model_descriptions = dict(self._fields['target_model']._description_selection(self.env))
            raise UserError(
                _("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average costing method.",
                  target_model_descriptions[self.target_model]))
        return lines

    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            cost = cost.with_company(cost.company_id)
            rounding = cost.currency_id.rounding
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_m2 = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)
                total_m2 += val_line_values.get('m2', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                total_cost += cost.currency_id.round(former_cost)
                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'by_m2' and total_m2:
                            per_unit = (line.price_unit / total_m2)
                            value = valuation.m2 * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if rounding:
                            value = tools.float_round(value, precision_rounding=rounding, rounding_method='HALF-UP')
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
                rounding_diff = cost.currency_id.round(line.price_unit - value_split)
                if not cost.currency_id.is_zero(rounding_diff):
                    towrite_dict[max(towrite_dict.keys())] += rounding_diff
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(
        SPLIT_METHOD,
        string='Split Method',
        required=True,
        help="Equal: Cost will be equally divided.\n"
             "By Quantity: Cost will be divided according to product's quantity.\n"
             "By Current cost: Cost will be divided according to product's current cost.\n"
             "By Weight: Cost will be divided depending on its weight.\n"
             "By Volume: Cost will be divided depending on its volume.\n"
             "By M²: Cost will be divided depending on its square meter area.")


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    m2 = fields.Float(
        'M²', default=0.0,
        digits='Product Unit of Measure',
        help="Square meter area calculated from product dimensions")
