from itertools import groupby
from operator import attrgetter
from odoo import models, fields, _, api


class GolfTournamentMode(models.Model):
    _inherit = "golf.tournament_mode"

    def _process_cards_choice(self,tournament):
        tournament.card_ids.write({'position':0, 'position_tied':False})
        cards = list(x for x in tournament.card_ids if x.net_score > 0)
        get_player = attrgetter('player_id.id')
        get_score = attrgetter('net_score')
        # groupby needs sorted data or it fails!
        cards = [sorted(v,key=get_score)[0] for l,v in groupby(sorted(cards,key=get_player), get_player)]
        print("cards2",cards)
        res = [list(v) for l,v in groupby(sorted(cards,key = get_score), get_score)]        
        #print("res",res)
        position = 1
        for tier in res:
            tied = len(tier) > 1
            for card in tier:
                card.position=position
                card.position_tied = tied
                print(card.player_id.name,card.net_score,card.position,card.position_tied)
            position +=1
        
    def _process_cards(self,tournament):
        print("CHOICE",self.code)
        if self.code == 'CHOICE':
            # process cards
            self._process_cards_choice(tournament)
            return None
        return super()._process_cards(tournament)

        
