from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class GolfCard(models.Model):
    _name = 'golf.card'
    _description = 'a golf card'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    date = fields.Date(string='Date')
    tournament_id = fields.Many2one('golf.tournament', 
        string='Tournament',
        required=True, 
        ondelete='cascade', 
        index=True,
        copy=False,
        default=lambda self: self._default_tournament_id(),
        )
    player_id = fields.Many2one('res.partner', string='Player', required=True, ondelete='cascade', index=True, copy=False, domain=[("golf_player", "=", True)])
    marker_id = fields.Many2one('res.partner', string='Marker', domain=[("golf_player", "=", True)])

    score_ids=fields.One2many("golf.score", 'card_id', string = "scores")

    gross_score=fields.Integer()
    net_score=fields.Integer()
    player_handicap = fields.Integer(string = 'Handicap', related = 'player_id.golf_handicap')

    def _default_tournament_id(self):
        tournament_ids = self.env["golf.tournament"].search(
            [],
            limit=1,
        )
        if tournament_ids:
            return tournament_ids[0]
        else:
            raise ValidationError(_("You must create an golf field first."))

    @api.onchange("score_ids")
    def _calculate_score(self):
        self.gross_score=sum(c.score for c in self.score_ids)
        if self.gross_score > 0:
            self.net_score=self.gross_score - self.player_id.golf_handicap
        else:
            self.net_score=0

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("golf.card")
        card =super(GolfCard, self).create(vals)
        if not len(card.score_ids) and card.tournament_id:
            for hole in card.tournament_id.get_holes():
                values={
                    'card_id': card.id,
                    'hole_id': hole.id,
                }
                self.env["golf.score"].sudo().create(values)
        return card

class GolfScore(models.Model):
    _name = 'golf.score'
    _description = 'a golf hole score'


    name = fields.Char(
        string="Name",
        required=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    
    card_id = fields.Many2one('golf.card', string='Card', required=True, ondelete='cascade', index=True, copy=False)
    hole_id = fields.Many2one('golf.hole', string='Hole', required=True, ondelete='cascade', index=True, copy=False)
    field_name = fields.Char(compute='_set_field_name', store=True )
    
    score = fields.Integer(string='Score')
    
    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("golf.score") or _("New")
        
        return super(GolfScore, self).create(vals)
    
    @api.depends("hole_id")
    def _set_field_name(self):
        for rec in self:
            print("set_field_name",rec.hole_id,rec.hole_id.field_id.name)
            rec.field_name = rec.hole_id.field_id.name
    
    def get_field_name(self):
        return self.hole_id.field_id.name