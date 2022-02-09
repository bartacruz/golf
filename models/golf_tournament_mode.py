
from odoo import models, fields, _, api

class GolfTournamentMode(models.Model):
    _name = 'golf.tournament_mode'
    _description = 'Tournament Mode'

    name = fields.Char()
    code = fields.Char(required=True)

    default = fields.Boolean(default=False)

    def _process_cards(self,tournament):
        return None



