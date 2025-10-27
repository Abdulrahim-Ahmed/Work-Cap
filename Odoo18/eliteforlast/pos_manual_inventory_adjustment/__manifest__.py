{
    'name': 'POS Manual Inventory Adjustment',
    'version': '18.0.3.0.0',
    'category': 'Point of Sale',
    'summary': 'Manual inventory adjustment from POS interface',
    'description': """
        This module allows users to create manual inventory adjustments from the POS interface.
        Features:
        - Create inventory adjustment sheets from POS Orders menu
        - Add products and counted quantities
        - Print sheets for signature
        - Submit to create standard inventory adjustments
    """,
    'depends': ['point_of_sale', 'stock', 'product', 'dvit_warehouse_stock_restrictions'],
    'data': [
        'security/pos_manual_inventory_security.xml',
        'security/ir.model.access.csv',
        'views/pos_manual_inventory_views.xml',
        'reports/inventory_count_sheet_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}