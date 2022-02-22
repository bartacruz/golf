
from odoo import models, fields, _, api

class GolfTournamentMode(models.Model):
    _name = 'golf.tournament_mode'
    _description = 'Tournament Mode'

    name = fields.Char()
    code = fields.Char(required=True)

    default = fields.Boolean(default=False)

    def _process_cards(self,tournament):
        return None

    def _set_positions(self,cards):
        position = 1
        for tier in cards:
            group_count = len(tier)
            tied = group_count > 1
            for card in tier:
                card.position=position
                card.position_tied = tied
            position += group_count
