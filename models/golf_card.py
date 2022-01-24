from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
import pytz


class GolfCard(models.Model):
    _name = 'golf.card'
    _description = 'a golf card'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    date = fields.Date(string='Date', default=fields.datetime.now().date())
    tournament_id = fields.Many2one('golf.tournament',
                                    string='Tournament',
                                    required=True,
                                    ondelete='cascade',
                                    index=True,
                                    copy=False,
                                    default=lambda self: self._default_tournament_id(),
                                    )
    player_id = fields.Many2one('res.partner', string='Player', required=True,
                                ondelete='cascade', index=True, copy=False, domain=[("golf_player", "=", True)])
    marker_id = fields.Many2one('res.partner', string='Marker', domain=[
                                ("golf_player", "=", True)])

    score_ids = fields.One2many("golf.score", 'card_id', string="scores")

    gross_score = fields.Integer(compute='_calculate_score', store=True)
    net_score = fields.Integer(compute='_calculate_score', store=True)
    
    player_handicap = fields.Integer(
        string='Handicap', related='player_id.golf_handicap')
    
    position = fields.Integer(default=0)
    position_tied = fields.Boolean()
    position_label = fields.Char(compute='_compute_position_label' , store=True)
    
    @api.depends('position','position_tied')
    def _compute_position_label(self):
        for record in self:
            if record.position > 0:
                tied = 'T' if record.position_tied else ''
                record.position_label = '%s%s' % (tied,record.position, )
                print(record.name,record.net_score,record.position_label)
    

    account_move_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)

    stage_id = fields.Many2one(
        "golf.cardstage",
        string="Stage",
        tracking=True,
        index=True,
        copy=False,
        default=lambda self: self._default_stage_id(),
    )

    def _default_stage_id(self):
        stage_ids = self.env["golf.cardstage"].search(
            [("is_default", "=", True),],
            order="sequence asc",
            limit=1,
        )
        if stage_ids:
            return stage_ids[0]
        else:
            raise ValidationError(_("You must create an golf stage first."))

    def _default_tournament_id(self):
        tournament_ids = self.env["golf.tournament"].search(
            [],
            order="date desc",
            limit=1,
        )
        if tournament_ids:
            return tournament_ids[0]
        else:
            raise ValidationError(_("You must create an golf field first."))

    @api.onchange('account_move_id')
    def check_stage(self):
        print("check_stage",self.stage_id.is_closed,self.account_move_id)
        if not self.stage_id.is_closed and self.account_move_id:
            stage = self.env["golf.cardstage"].search(
            [("name", "=", 'Active'),],
            limit=1,)
            print("stage:",stage)
            if len(stage):
                self.stage_id=stage[0]

    @api.depends("score_ids")
    def _calculate_score(self):
        for rec in self:
            net = rec.net_score # save it to detect changes
            rec.gross_score = sum(c.score for c in rec.score_ids)
            if rec.gross_score > 0:
                rec.net_score = rec.gross_score - rec.player_id.golf_handicap
            else:
                rec.net_score = 0

            if net != rec.net_score:
                rec.tournament_id.action_leaderboard()

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("golf.card")
        card = super(GolfCard, self).create(vals)
        if not len(card.score_ids) and card.tournament_id:
            for hole in card.tournament_id.get_holes():
                values = {
                    'card_id': card.id,
                    'hole_id': hole.id,
                }
                self.env["golf.score"].sudo().create(values)
        return card

    def action_view_invoice(self):
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["views"] = [(self.env.ref("account.view_move_form").id, "form")]
        action["res_id"] = self.account_move.id
        return action

    def action_golf_card_invoice(self):
        self.ensure_one()
        timezone = pytz.timezone(self._context.get(
            'tz') or self.env.user.tz or 'UTC')

        # TODO: use categories for products
        product = self.tournament_id.default_product_id
        player = self.player_id 
        if player.property_product_pricelist:
            price = player.property_product_pricelist.get_product_price(product,1,player)
            name = '%s - %s' % (product.display_name,player.property_product_pricelist.name,)
        else:
            price = product.list_price
            name = product.name
        invoice_line = {
            'product_id': product.id,
            'quantity': 1,
            'price_unit': price,
            'name': name,
            'tax_ids': [(6, 0, product.taxes_id.ids)],
        }
        narration = '%s - %s' % (product.display_name, self.tournament_id.name,)
        move_vals = {
            'payment_reference': self.name,
            'invoice_origin': self.tournament_id.name,
            'state' : 'draft',
            'move_type': 'out_invoice',
            'ref': self.name,
            'partner_id': player.id,
            'narration': narration,
            'invoice_user_id': self.env.context.get('user_id', self.env.user.id),
            'invoice_date': self.date,
            'invoice_line_ids': [(0, None, invoice_line)],
            
        }

        new_move = self.env['account.move'].sudo().with_context(
                    default_move_type=move_vals['move_type']).create(move_vals)
        self.write({'account_move_id': new_move.id})
        self.check_stage()
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': new_move.id,
        }


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

    card_id = fields.Many2one('golf.card', string='Card',
                              required=True, ondelete='cascade', index=True, copy=False)
    hole_id = fields.Many2one('golf.hole', string='Hole',
                              required=True, ondelete='cascade', index=True, copy=False)
    field_name = fields.Char(compute='_set_field_name', store=True)

    score = fields.Integer(string='Score')

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "golf.score") or _("New")

        return super(GolfScore, self).create(vals)

    @api.depends("hole_id")
    def _set_field_name(self):
        for rec in self:
            print("set_field_name", rec.hole_id, rec.hole_id.field_id.name)
            rec.field_name = rec.hole_id.field_id.name

    def get_field_name(self):
        return self.hole_id.field_id.name

class GolfCardStage(models.Model):
    _name = "golf.cardstage"
    _description = "Golf Card Stage"
    _order = "sequence, name, id"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(
        "Sequence", default=1, help="Used to order stages. Lower is better."
    )
    is_closed = fields.Boolean(
        "Is a close stage", help="Services in this stage are considered " "as closed."
    )
    is_default = fields.Boolean("Is a default stage", help="Used a default stage")
    custom_color = fields.Char(
        "Color Code", default="#FFFFFF", help="Use Hex Code only Ex:-#FFFFFF"
    )
    description = fields.Text(translate=True)
    
    @api.constrains("custom_color")
    def _check_custom_color_hex_code(self):
        if (
            self.custom_color
            and not self.custom_color.startswith("#")
            or len(self.custom_color) != 7
        ):
            raise ValidationError(_("Color code should be Hex Code. Ex:-#FFFFFF"))
