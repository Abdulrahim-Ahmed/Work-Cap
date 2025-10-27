{
    'name': 'Product Variant Display Name',
    'version': '18.0.1.0.0',
    'category': 'Product',
    'summary': 'Show variant display name in product list view',
    'description': """
        This module adds the variant display_name field to the product tree view
        to better identify product variants.
    """,
    'author': 'capstone-solution',
    'depends': ['product'],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
