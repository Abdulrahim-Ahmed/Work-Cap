{
    "name": "Stock Product Catalog",
    "summary": "Use the product catalog on stock pickings",
    "version": "18.0.1.0.0",
    "author": "Capstone Solutions",
    "website": "https://www.capstonesolutions.com",
    # "license": "AGPL-3",
    "category": "Product",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_views.xml",
        "views/stock_picking_type_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "product_catalog_stock/static/src/**/*",
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
