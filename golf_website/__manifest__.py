# -*- coding: utf-8 -*-
{
    'name': "Golf Club Website",

    'summary': "Website addons for golf clubs",
    'sequence': -100,
    'description': """
        Module for managing website addons for golf clubs.
    """,

    'author': "BartaTech",
    'website': "http://www.bartatech.com",

    'category': 'Sports',
    'version': '16.0.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['golf', 'website'],

    # always loaded
    'data': [
        # 'views/golf_field.xml',
        # 'views/golf_card.xml',
        # 'views/golf_player.xml',
        # 'views/golf_tournament.xml',
        # 'views/golf_cardstage.xml',
        'views/res_partner_portal.xml',
        'views/website_golf.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    "development_status": "Alpha",

    'assets': {
        'web.assets_frontend': [
            'golf_website/static/src/css/golf.scss',
        ],
    },
}
