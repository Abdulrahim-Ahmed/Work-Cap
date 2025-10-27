# -*- coding: utf-8 -*-
{
    'name': "edit sale v15",
    'summary': """        add cost in line """,
    'description': """  edit order sales line and but cost in line 
                        make validation worrying for price upper than cost or lower   
                        put field total to effect on price before vat
                         hide purchase page for all exception user add for them    """,
    'author': "My Company",
    'website': "http://www.deverst.co",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'depends': ['base', 'sale_management', 'product', 'stock','sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/see_purchase_page.xml',
        'views/views.xml',
        'views/res_config_view.xml',
        'views/menu_stock.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
