# -*- coding: utf-8 -*-
{
    'name': "Journal Analytic Account",

    'summary': "This Model Is Adding Analytic Account Field Into Journals",

    'description': """
This Model Is Adding Analytic Account Field Into Journals
    """,

    'author': "Capstone Solutions",
    'website': "https://www.capstone-solution.com",
    'category': 'Uncategorized',
    'version': '18.0',
    'depends': ['base', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

