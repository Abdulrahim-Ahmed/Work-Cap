# -*- coding: utf-8 -*-
{
    'name': "Print Invoice",
    'summary': """""",
    'description': """""",
    'author': "Abd Elhamed Saad",
    'website': "https://www.linkedin.com/in/abd-elhamed-saad/",
    'category': 'Services',
    'version': '16.0.1',
    'license': "AGPL-3",
    'depends': ['base', 'account', 'l10n_sa', ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/report_docs.xml',
        'report/tax_invoice.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.report_assets_common': [
            'print_invoice/static/src/css/style_print.css',
        ],
    },
}
