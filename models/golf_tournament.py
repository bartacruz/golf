from datetime import datetime
from pprint import pprint
import re
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from itertools import chain, groupby
from operator import attrgetter
from . import aag_api
class GolfTournament(models.Model):
    _name = 'golf.tournament'
    _description = 'a golf tournament'
    _inherit = [
        'website.published.mixin',
        'mail.thread', 
        'mail.activity.mixin'
    ]

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    date = fields.Date(string=_('Date'))
    parent_id = fields.Many2one('golf.tournament')
    child_ids = fields.One2many('golf.tournament', 'parent_id')
    field_ids = fields.Many2many(
        string=_('Fields'),
        comodel_name='golf.field',
    )
    field_id = fields.Many2one(
        string=_('Field'),
        comodel_name='golf.field',
    )

    notes = fields.Text(_("Notes"))

    card_ids = fields.One2many('golf.card','tournament_id',string=_('Cards'))
    card_count = fields.Integer(compute = '_count_cards')
    active_card_count = fields.Integer(compute = '_count_cards')
    player_ids = fields.Many2many('res.partner', string='Players', domain=[("golf_player", "=", True)])

    default_product_id = fields.Many2one(
        string='Default Product',
        comodel_name='product.template',
        ondelete='restrict',
    )
    tournament_mode_id = fields.Many2one('golf.tournament_mode', string = _('Mode'))
    
    external_reference = fields.Integer()
    posted = fields.Boolean(string=_('Posted')) # posted to AAG
    
    state = fields.Selection(selection=[
            ('new', 'New'),
            ('active', 'Active'),
            ('finished', 'Finished'),
            ('cancelled', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='new')
    
    category = fields.Selection(selection=[('0','Caballeros'),('1','Damas')], default='0')
    
    @api.onchange('date')
    def _default_product(self):
        if not self.date:
            return
        if self.date.weekday() > 4:
            self.default_product_id = int(self.env['ir.config_parameter'].sudo().get_param('golf.tournament_product_weekend'))
        else:
            self.default_product_id = int(self.env['ir.config_parameter'].sudo().get_param('golf.tournament_product'))
    
    def action_activate(self):
        for record in self:
            self.state = 'active'
            self.website_published = True
            self.message_post(body=_('Tournament activated'))
    
    def action_finish(self):
        for record in self:
            self.state = 'finished'
            self.message_post(body=_('Tournament finished'))

    def action_cancel(self):
        for record in self:
            self.state = 'cancelled'
            self.website_published = False
            self.message_post(body=_('Tournament cancelled'))
    
    @api.depends('card_ids')
    def _count_cards(self):
        for rec in self:
            rec.card_count = len(rec.card_ids)
            rec.active_card_count = len([x for x in rec.card_ids if x.net_score > 0])
            rec.player_ids = rec.mapped("card_ids.player_id")
    
    def _check_name(self):
        for record in self:
            if record.name == _('New') or record.name == 'SPGC' and record.tournament_mode_id:
                record.name = '%s - %d hoyos' % (record.tournament_mode_id.name, record.field_id.hole_count,)
                print("_check_name",record.name)

    def post_external(self):
        if not self.tournament_mode_id or not self.tournament_mode_id.external_reference:
            print("No se puede postear un torneo con un modo no soportado por AAG")
            return False
        # Torneo guardado correctamente con id: 93802{"Description":"Proceso ","ProcessStart":"2022-09-22T13:35:44.9020323-03:00","ProcessEnd":"2022-09-22T13:35:44.9020323-03:00","HasError":false,"Errors":[],"Comments":[]}
        cards = []
        data = {
            'Id': self.id,
            'Title': self.name,
            'Subtitle': self.name,
            'GameMode': self.tournament_mode_id.external_reference,
            'BatchesCount': 1, # TODO: harcoded (numero de vueltas)
            'BatchesHoles': self.field_id.hole_count,
            'Category': int(self.category),
            'EndHandicap': 54,
            'StartDate': datetime(self.date.year, self.date.month, self.date.day).isoformat(),
            'Field': self.field_id.external_reference,
            'TeeOut': 4532,
            'Active': self.state == 'active',
            'ScoreCards': cards,
        }
        
        posted_cards = self.card_ids.filtered(lambda card: card.player_id.golf_license_active and not card.posted)
        
        for card in posted_cards:
            if card.player_id.golf_license_active and not card.posted:
                cards.append(card.get_external_data())
        
        print(data)
        response = aag_api.post_tournament(data)
        print('response',response)
        # TODO: retornar un mensaje de ok/error o algo similar
        if type(response) == str:
            rr = re.search(r'Torneo guardado correctamente con id: (\d+)',response)
            if rr:
                self.external_reference = rr[1]
                self.posted=True
                posted_cards.posted = True
                posted_cards.message_post(body=_('Card posted'))
                self.message_post(body=_('Tournament posted'))
                return True
        else:
            print('hasError',response.keys(),response.get('HasError'))
        
        return False

    def fetch_tournament(self,tid=None):
        self.ensure_one()
        
        if not self.external_reference:
            return False
        
        t =aag_api.get_tournament(self.external_reference)
        print(t)
        self.tournament_mode_id = self.env['golf.tournament_mode'].search([('external_reference','=',t.get('GameMode'))]).id
        self.date = t.get('StartDate')
        # TODO: chequear si se puede crear en la AAG un campo para 9 hoyos.
        if t.get('BatchesHoles',0) == 9:
            self.field_id = int(self.env['ir.config_parameter'].sudo().get_param('golf.default_field_9'))
        else:
            self.field_id = self.env['golf.field'].search([('external_reference','=',t.get('Field'))]).id
        
        # Hack para los que tienen titulo generico
        if t.get('Title') == 'SPGC':
            self._check_name()
        else:
            self.name = t.get('Title')
        
        if t.get('Active',False):
            self.state = 'active'
        else:
            self.state = 'finished'
    
        self.posted = True
        
        for card in t.get('ScoreCards'):
            if card.get('Status') not in ['Original','Ajuste']:
                continue
            player = self.env['res.partner'].search([('golf_license','=',card.get('EnrollmentNumber'))])
            if not player:
                print("creando desde aag",card.get('EnrollmentNumber'))
                player = self.env['res.partner'].create_from_external(card.get('EnrollmentNumber'))
            vals={
                'external_reference': card.get('Id'),
                'tournament_id': self.id,
                'player_id': player.id,
            }
            scorecard = self.env['golf.card'].create(vals)
            scorecard._set_handicap()
            
            for hole,score in {k:v for k,v in card.items() if k.startswith('ScoreGrossHole')}.items():
                hole_number=int(hole.replace('ScoreGrossHole',''))
                scorecard.set_score(hole_number,score)
            
        self.action_leaderboard()
        return self
    
    @api.model
    def create(self,vals):
        tournament = super(GolfTournament, self).create(vals)
        if vals.get("name", _("New")) == _("New"):
            tournament._check_name()
        return tournament
    
    def write(self, vals):
        t =  super().write(vals)
        if self.name== _("New"):
            self._check_name()
        return t
        
    def get_holes(self):
        holes = list(self.field_id.hole_ids)
        return holes

    def action_print_leaderboard(self):
        for tournament in self:
            print("PRINT LEADERBOARD",tournament)
                
    def action_open_leaderboard(self):
        for tournament in self:
            action = self.env.ref("golf.action_golf_leaderboard_act_window").read()[0]
            action["context"] = {}
            action["domain"] = ['&',("id", "in", tournament.card_ids.ids),("position",">",0)]
            return action

    def get_leaderboard(self):
        self.ensure_one()
        GolfCard = self.env['golf.card']
        leaderboard = sorted(GolfCard.sudo().search([('tournament_id','=',self.id),('position','>',0)]),key=lambda x: x.position)
        return leaderboard

    @api.onchange("card_ids")
    def action_leaderboard(self):
        self.tournament_mode_id._process_cards(self)

    