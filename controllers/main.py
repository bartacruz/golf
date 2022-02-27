from odoo import http
from odoo.http import request


class Golf(http.Controller):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'invoice_count' in counters:
            invoice_count = request.env['account.move'].search_count(self._get_invoices_domain()) \
                if request.env['account.move'].check_access_rights('read', raise_exception=False) else 0
            values['invoice_count'] = invoice_count
        return values

    @http.route(['/golf'], type='http', auth="public", website=True)
    def tournaments(self, **post):
        Tournament = request.env['golf.tournament']
        tournaments = Tournament.sudo().search([], order='date desc')
        values = {'tournaments': tournaments}
        return request.render("golf.tournaments", values)

    @http.route(['/golf/tournament/<model("golf.tournament"):tournament>'], type='http', auth="public", website=True)
    def tournament(self, tournament=None, **post):
        leaderboard = tournament.get_leaderboard()
        values = {'tournament': tournament, 'leaderboard': leaderboard}
        return request.render("golf.tournament", values)


    @http.route(['/golf/card/<model("golf.card"):card>'], type='http', auth="public", website=True)
    def card(self, card=None, **post):
        values = {'card': card, }
        return request.render("golf.card", values)
    
    @http.route(['/golf/player/<model("res.partner"):player>'], type='http', auth="public", website=True)
    def player(self, player=None, **post):
        values = {'player': player, }
        return request.render("golf.player", values)
