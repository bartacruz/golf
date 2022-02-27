# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class PortalGolf(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'golfcards_count' in counters:
            card_count = request.env['golf.card'].search_count([('player_id','=',partner.id)]) \
                if request.env['golf.card'].check_access_rights('read', raise_exception=False) else 0
            values['golfcards_count'] = card_count
            print(values)
        return values

    @http.route(['/my/golfcards', '/my/golfcards/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_golfcards(self, page=1, **kw):
    #def portal_my_golfcards(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        GolfCard = request.env['golf.card']

        domain = [('player_id','=',partner.id)]
        cards_count = GolfCard.search_count(domain) 

        pager = portal_pager(
            url="/my/golfcards",
            # url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=cards_count,
            page=page,
            step=self._items_per_page
        )
        cards = GolfCard.search(domain,  limit=self._items_per_page, offset=pager['offset'])
        request.session['my_golfcards_history'] = cards.ids[:100]
        values.update({
            # 'date': date_begin,
            'cards': cards,
            'page_name': 'golfcards',
            'pager': pager,
            'default_url': '/my/golfcards',
            #'searchbar_sortings': searchbar_sortings,
            #'sortby': sortby,
            #'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            #'filterby':filterby,
        })
        return request.render("golf.portal_my_golfcards", values)
