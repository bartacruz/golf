from itertools import groupby
from operator import attrgetter
from odoo import models, fields, _, api


class GolfTournamentMode(models.Model):
    _inherit = "golf.tournament_mode"

    def _process_cards_choice(self,tournament):
        cards = list(x for x in tournament.card_ids if x.gross_score > 0)
        #gross = sorted(cards,key=lambda x: x.net_score, reverse=True)
        get_gross = attrgetter('gross_score')
        res = [list(v) for l,v in groupby(sorted(cards,key = get_gross), get_gross)]        
        position = 1
        for tier in res:
            tied = len(tier) > 1
            for card in tier:
                card.position=position
                card.position_tied = tied
                #print(card.player_id.name,card.net_score,card.position,card.position_tied)
            position +=1
        
    def _process_cards(self,tournament):
        print("CHOICE",self.code)
        if self.code == 'CHOICE':
            # process cards
            self._process_cards_choice(tournament)
            return None
        return super()._process_cards(tournament)

        
