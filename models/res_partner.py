from odoo import _,fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    golf_player = fields.Boolean("Is a golf player")
    golf_license = fields.Integer(
        string='golf license',
    )
    golf_handicap = fields.Integer(
        string='handicap',
    )
    golf_card_ids = fields.One2many(
        'golf.card',
        'player_id',
        string=_('Cards')
    )
    golf_card_count = fields.Integer(compute = '_golf_count_cards')

    golf_membership = fields.Many2one(
        string='Membership',
        comodel_name='product.template',
        ondelete='restrict',
    )

    def _golf_count_cards(self):
        for rec in self:
            rec.golf_card_count = len(rec.golf_card_ids)
    
    def action_open_golf_cards(self):
        for rec in self:
            action = self.env.ref("golf.action_golf_card_act_window").read()[0]
            action["context"] = {}
            action["domain"] = [("id", "in", rec.golf_card_ids.ids)]
            return action