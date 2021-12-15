from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from itertools import chain, groupby
from operator import attrgetter
class GolfTournament(models.Model):
    _name = 'golf.tournament'
    _description = 'a golf tournament'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    date = fields.Date(string=_('Date'))

    field_ids = fields.Many2many(
        string=_('Fields'),
        comodel_name='golf.field',
    )

    card_ids = fields.One2many('golf.card','tournament_id',string=_('Cards'))
    card_count = fields.Integer(compute = '_count_cards')

    default_product_id = fields.Many2one(
        string='Default Product',
        comodel_name='product.template',
        ondelete='restrict',
    )
    
    def _count_cards(self):
        for rec in self:
            rec.card_count = len([x for x in rec.card_ids if x.net_score > 0])
    
    def get_holes(self):
        holes = []
        for field in self.field_ids:
            holes += list(field.hole_ids)
        print("holes",holes)
        return holes
        
    def action_open_leaderboard(self):
        for tournament in self:
            action = self.env.ref("golf.action_golf_leaderboard_act_window").read()[0]
            action["context"] = {}
            action["domain"] = ['&',("id", "in", tournament.card_ids.ids),("net_score",">",0)]
            return action

    @api.onchange("card_ids")
    def action_leaderboard(self):
        cards = list(x for x in self.card_ids if x.net_score > 0)
        #gross = sorted(cards,key=lambda x: x.net_score, reverse=True)
        print("cards:",cards,[x.net_score for x in cards])
        get_net = attrgetter('net_score')
        res = [list(v) for l,v in groupby(sorted(cards,key = get_net), get_net)]
        print("grouped:",res)
        
        position = 1
        for tier in res:
            tied = len(tier) > 1
            for card in tier:
                card.position=position
                card.position_tied = tied
                print(card.player_id.name,card.net_score,card.position,card.position_tied)
            position +=1


