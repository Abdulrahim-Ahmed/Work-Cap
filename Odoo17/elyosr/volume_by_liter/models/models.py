# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VolumeInProduct(models.Model):
    _inherit = 'product.template'

    volume_by_liter = fields.Float(string="Volume By Liter", required=False, store=True)
    volume = fields.Float(
        'Volume', compute='_compute_volume', inverse='_set_volume', digits=(16, 3), store=True)

    @api.onchange('volume_by_liter')
    def _onchange_volume_by_liter(self):
        """ Convert liters to cubic meters (divide by 1000) and update the volume field. """
        for record in self:
            if record.volume_by_liter:
                record.volume = record.volume_by_liter / 1000

    @api.onchange('volume')
    def _onchange_volume(self):
        """ Convert cubic meters to liters (multiply by 1000) and update the volume_by_liter field. """
        for record in self:
            if record.volume:
                record.volume_by_liter = record.volume * 1000


class VolumeByLiterSalesPivot(models.Model):
    _inherit = 'sale.report'

    volume_by_liter = fields.Float(string="Volume By Liter", required=False,
                                   readonly=True, store=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['volume_by_liter'] = "SUM(l.product_uom_qty * t.volume_by_liter)"
        return res


class VolumeByLiterPurchasePivot(models.Model):
    _inherit = 'purchase.report'

    volume_by_liter = fields.Float(related='product_id.volume_by_liter', string="Volume By Liter", required=False,
                                   readonly=True, store=True)
    volume = fields.Float(
        'Volume', compute='_compute_volume', inverse='_set_volume', digits=(16, 3), store=True)

    def _select(self):
        select_str = """
                SELECT
                    po.id as order_id,
                    min(l.id) as id,
                    po.date_order as date_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_id as partner_id,
                    po.user_id as user_id,
                    po.company_id as company_id,
                    po.fiscal_position_id as fiscal_position_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    c.currency_id,
                    t.uom_id as product_uom,
                    extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as price_total,
                    (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) * currency_table.rate as price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
                    sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
                    sum(t.volume_by_liter * l.product_qty/line_uom.factor*product_uom.factor) as volume_by_liter,
                    sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as untaxed_total,
                    sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
                    sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
                    sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
                    case when t.purchase_method = 'purchase' 
                         then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                         else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                    end as qty_to_be_billed
        """
        return select_str


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    volume_by_liter = fields.Float(string="Volume By Liter", required=False,
                                   readonly=True, store=True)
    weight = fields.Float(string="Weight", required=False, readonly=True, store=True)

    # def _select(self):
    #     parent_select = super()._select() or ""
    #     return f"""{parent_select}
    #         , template.volume_by_liter
    #         , template.weight
    #     """
    #
    # def _group_by(self):
    #     parent_group_by = super()._group_by() or ""
    #     return f"""{parent_group_by}
    #         , template.volume_by_liter
    #         , template.weight
    #     """

    def _select(self):
        parent_select = super()._select() or ""
        return f"""{parent_select}
            , (template.volume_by_liter * line.quantity) AS volume_by_liter
            , (template.weight * line.quantity) AS weight
        """

    def _group_by(self):
        parent_group_by = super()._group_by() or ""
        # no need to group by template fields anymore, since they're aggregated
        return parent_group_by