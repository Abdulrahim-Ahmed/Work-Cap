from odoo import models, fields, api


class ProductVariantSearchWizard(models.TransientModel):
    _name = "product.variant.search.wizard"
    _description = "Advanced Variant Search"

    line_ids = fields.One2many(
        'product.variant.search.wizard.line',
        'wizard_id',
        string="Attribute Filters"
    )

    def action_search(self):
        """Return an action that filters product variants by all selected attribute values"""
        self.ensure_one()
        domain = []
        for line in self.line_ids:
            if line.value_id:
                domain.append(
                    ('product_template_attribute_value_ids.product_attribute_value_id', '=', line.value_id.id))
        return {
            'name': 'Product Variants',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': domain,
            'context': dict(self.env.context),
        }


class ProductVariantSearchWizardLine(models.TransientModel):
    _name = "product.variant.search.wizard.line"
    _description = "Product Variant Search Wizard Line"

    wizard_id = fields.Many2one('product.variant.search.wizard', required=True)
    attribute_id = fields.Many2one('product.attribute', string="Attribute", required=True)
    value_id = fields.Many2one(
        'product.attribute.value',
        string="Attribute Value",
        required=True,
        domain="[('attribute_id', '=', attribute_id)]"
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            # Split by whitespace (default Odoo behavior is OR, we force AND)
            search_terms = [term.strip() for term in name.split() if term.strip()]
            for term in search_terms:
                args.append((
                    "product_template_attribute_value_ids.name",
                    operator,
                    term
                ))
            # Clear `name` so Odoo doesn’t build its own OR domain
            name = ""

        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    # @api.model
    # def name_search(self, name="", args=None, operator="ilike", limit=100):
    #     args = args or []
    #
    #     if name and "," in name:
    #         # Split by comma, trim spaces
    #         search_terms = [term.strip() for term in name.split(",") if term.strip()]
    #
    #         # For each term, add an AND condition
    #         for term in search_terms:
    #             args.append(("product_template_attribute_value_ids.name", "ilike", term))
    #
    #         # clear the original `name` because we already expanded it
    #         name = ""
    #
    #     return super().name_search(name=name, args=args, operator=operator, limit=limit)