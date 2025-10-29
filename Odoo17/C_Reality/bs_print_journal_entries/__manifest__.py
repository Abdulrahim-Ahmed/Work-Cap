# -*- coding: utf-8 -*-

{
    'name': 'Print Journal Entries Report in Odoo',
    'version': '17.0.0.0',
    'category': 'Accounting',
    'license': 'OPL-1',
    'summary': 'Allow to print pdf report of Journal Entries.',
    'description': """
    Allow to print pdf report of Journal Entries.
    journal entry
    print journal entry 
    journal entries
    print journal entry reports
    account journal entry reports
    journal reports
    account entry reports

    
""",
    "author": "Boom solutions co",
    'website': "https://www.boom-solutions.co",
    "support": "info@capstone solution",
    'depends': ['base','account'],
    'data': [
            'report/report_journal_entries.xml',
            'report/report_journal_entries_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":["static/description/icon.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
