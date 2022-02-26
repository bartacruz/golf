from odoo import http
from odoo.http import request


class Golf(http.Controller):

    @http.route(['/golf'], type='http', auth="public", website=True)
    def tournaments(self, **post):
        Tournament = request.env['golf.tournament']
        tournaments = Tournament.search([])
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
