# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """Update the security rule to use company_ids instead of user.company_id.id"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Find the security rule
    rule = env['ir.rule'].search([
        ('model_id.model', '=', 'pos.order.cancel'),
        ('name', 'like', 'POS Order Cancel%')
    ], limit=1)
    
    if rule:
        # Update the domain to use company_ids
        rule.write({
            'domain_force': "[('company_id', 'in', company_ids)]",
            'name': 'POS Order Cancel: User allowed companies'
        })
        cr.commit()
