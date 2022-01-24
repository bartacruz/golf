# -*- coding: utf-8 -*-
{
    'name': "Golf Club",

    'summary': "Golf Club Module",
    'sequence': -100,
    'description': """
        Supercalifragilistico long description
    """,

    'author': "BartaTech",
    'website': "http://www.bartatech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sports',
    'version': '15.0.0.1.4',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        #'views/assets.xml',
        'views/golf_field.xml',
        'views/golf_card.xml',
        'views/golf_player.xml',
        'views/golf_tournament.xml',
        'views/golf_cardstage.xml',
        'views/res_partner.xml',
        'views/menu.xml',
        'reports/golf_card_report.xml',
        #'views/menu.xml',
        #'views/res_partner.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    "development_status": "Alpha",
    'images': ['static/description/golf-icon.png'],
    'assets': {
        'web.assets_backend': [
            'golf/static/src/js/golf_card_widget.js',
            'golf/static/src/css/golf.scss',
        ],
        'web.report_assets_common': [
            'golf/static/src/css/card.scss',
        ],
    },
}
