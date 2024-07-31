from odoo import models, fields, _, api
class GolfTournament(models.Model):
    _name = 'golf.tournament'
    _inherit = [
        'golf.tournament'
        'website.published.mixin'
    ]

    def _activate(self):
        self.ensure_one()
        super(GolfTournament, self)._activate()
        self.website_published = True

    def _cancel(self):
        super(GolfTournament, self)._cancel()
        self.website_published = False

    @api.depends('name')
    def _compute_website_url(self):
        super(GolfTournament, self)._compute_website_url()
        for tournament in self:
            if tournament.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                tournament.website_url = '/golf/tournament/%s' % slug(tournament)
    
    def action_toggle_website_published(self):
        for record in self:
            record.website_published =  not record.website_published
