from odoo import _,fields, models, api
import datetime
import uuid
from . import aag_api

class ResPartner(models.Model):
    _inherit = "res.partner"

    golf_player = fields.Boolean("Is a golf player")
    golf_license = fields.Integer(
        string=_('Golf license'),
    )
    golf_license_active = fields.Boolean(_('License is active'))
    golf_handicap = fields.Integer(
        string=_('Handicap'),
    )
    
    golf_handicap_index = fields.Float(
        string=_("Handicap Index"),
        digits=(4,2),
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

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('golf_license', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super().name_search(name=name, args=args, operator=operator, limit=limit)
        return recs.name_get_for_search()
    
    def name_get_for_search(self):
        res = []
        for partner in self:
            name = partner._get_name()
            if partner.golf_license:
                name = '%s (%s)' % (name,partner.golf_license)
            res.append((partner.id, name))
        return res
    
    def _golf_count_cards(self):
        for rec in self:
            rec.golf_card_count = len(rec.golf_card_ids)
    
    def action_open_golf_cards(self):
        for rec in self:
            action = self.env.ref("golf.action_golf_card_act_window").read()[0]
            action["context"] = {}
            action["domain"] = [("id", "in", rec.golf_card_ids.ids)]
            return action

    def create_from_external(self,golf_license):
        player = aag_api.get_enrolled(golf_license)
        if not player:
            return
        # {'EnrollmentNumber': '101261', 'Active': True, 'FirstNames': 'JULIO', 'LastNames': 'SANTA CRUZ ', 'HandicapStandard': -99, 'HandicapEven3': -99, 'HandicapIndex': 15.6, 'LowestHandicapIndex': 18.1, 'OptionClubId': 365, 'Category': 0, 'BornDate': '27-8-1971', 'DocNumber': '22278642'}
        partner = self.search([
            ('firstname','ilike',player.get('FirstNames')),
            ('lastname','ilike',player.get('LastNames')),
        ])
        if not partner:
            partner = self.create({
                'firstname': player.get('FirstNames').title(),
                'lastname': player.get('LastNames').title(),
            })
            print("nuevo jugador",partner.name, player)
            
        partner.golf_license = int(player.get('EnrollmentNumber'))
        partner.update_from_external(player)
    
        return partner
            
            
    def update_from_external(self,data):
        self.ensure_one()
        print('update_from_external',data)
        if not data:
            self.golf_license_active=False
            return
        self.golf_player = True
        self.golf_license_active = data.get('Active')
        self.golf_handicap_index = data.get('HandicapIndex')
        self.golf_handicap = aag_api.get_handicap(self.golf_handicap_index)
        if not self.golf_membership:
            club = int(self.env['ir.config_parameter'].sudo().get_param('golf.club_id'))
            if data.get('OptionClubId',0) == club:
                membership = int(self.env['ir.config_parameter'].sudo().get_param('golf.default_product'))
                self.golf_membership =  membership
        if not self.l10n_ar_afip_responsibility_type_id:
            self.l10n_ar_afip_responsibility_type_id = int(self.env['ir.config_parameter'].sudo().get_param('golf.default_responsibility'))
        if not self.vat:
            try:
                self.l10n_latam_identification_type_id = int(self.env['ir.config_parameter'].sudo().get_param('golf.default_identification_type'))
                self.vat = data.get('DocNumber')
            except:
                print("Error al setear el dni de ",self.name,': ', data.get('DocNumber'))
        
        
    def action_update_handicap(self):
        for record in self:
            if record.golf_license:
                # get data from AAG
                data = aag_api.get_enrolled(record.golf_license)
                record.update_from_external(data)
                
    def action_golf_membership_invoice(self):
        """ Generates golf membership invoices for selected records"""
        ref = str(uuid.uuid4())[:8]
        for rec in self:
            # timezone = pytz.timezone(self._context.get(
            #     'tz') or self.env.user.tz or 'UTC')

            product = rec.golf_membership
            invoice_line = {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': product.list_price,
                'name': product.display_name,
                'tax_ids': [(6, 0, product.taxes_id.ids)],
            }
            narration = product.display_name + " - " + datetime.date.today().strftime("%B")
            move_vals = {
                'payment_reference': ref,
                'invoice_origin': product.name,
                'state' : 'draft',
                'move_type': 'out_invoice',
                'ref': ref,
                'partner_id': rec.id,
                'narration': narration,
                'invoice_user_id': self.env.context.get('user_id', self.env.user.id),
                'invoice_date': datetime.date.today(),
                'invoice_line_ids': [(0, None, invoice_line)],
                
            }
            
            new_move = self.env['account.move'].sudo().with_context(
                default_move_type=move_vals['move_type']).create(move_vals)
            
        return {
            'name': _('Golf Memberships %s' % ref),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_out_invoice_tree').id,
            'res_model': 'account.move',
            'context': "{'ref':'%s'}" % ref,
            'domain': [('ref', '=', ref)],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }