# -*- coding: utf-8 -*-
{
    'name': "Golf Club",

    'summary': "Golf Club Module",
    'sequence': -100,
    'description': """
        Module for managing a Golf Club, players, fields, tournaments and cards.
    """,

    'author': "BartaTech",
    'website': "http://www.bartatech.com",

    'category': 'Sports',
    'version': '15.0.0.1.11',

    # any module necessary for this one to work correctly
    'depends': ['base','website','mail','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/website_golf_security.xml',
        'data/ir_sequence.xml',
        'views/golf_field.xml',
        'views/golf_card.xml',
        'views/golf_player.xml',
        'views/golf_tournament.xml',
        'views/golf_cardstage.xml',
        'views/res_partner.xml',
        'views/menu.xml',
        'views/website_golf.xml',
        'reports/golf_card_report.xml',
        'data/tournament_modes.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    "development_status": "Alpha",
#    'images': ['static/description/golf-icon.png'],
    'assets': {
        'web.assets_backend': [
            'golf/static/src/js/golf_card_widget.js',
            'golf/static/src/css/golf.scss',
        ],
        'web.report_assets_common': [
            'golf/static/src/css/card.scss',
        ],
        'web.assets_frontend': [
            'golf/static/src/css/golf.scss',
        ],
    },
}
