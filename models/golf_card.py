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

    date = fields.Date(string='Date')
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

    gross_score = fields.Integer()
    net_score = fields.Integer()
    player_handicap = fields.Integer(
        string='Handicap', related='player_id.golf_handicap')
    
    account_move = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)

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
            order="date asc",
            limit=1,
        )
        if tournament_ids:
            return tournament_ids[0]
        else:
            raise ValidationError(_("You must create an golf field first."))

    @api.onchange('account_move')
    def check_stage(self):
        print("check_stage",self.stage_id.is_closed,self.account_move)
        if not self.stage_id.is_closed and self.account_move:
            stage = self.env["golf.cardstage"].search(
            [("name", "=", 'Active'),],
            limit=1,)
            print("stage:",stage)
            if len(stage):
                self.stage_id=stage[0]


    @api.onchange("score_ids")
    def _calculate_score(self):
        self.gross_score = sum(c.score for c in self.score_ids)
        if self.gross_score > 0:
            self.net_score = self.gross_score - self.player_id.golf_handicap
        else:
            self.net_score = 0

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
        invoice_line = {
            'product_id': product.id,
            'quantity': 1,
            'price_unit': product.list_price,
            'name': product.display_name,
            'tax_ids': [(6, 0, product.taxes_id.ids)],
        }
        narration = product.display_name + " - " + self.tournament_id.name
        move_vals = {
            'payment_reference': self.name,
            'invoice_origin': self.tournament_id.name,
            'state' : 'draft',
            #'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'move_type': 'out_invoice',
            'ref': self.name,
            'partner_id': self.player_id.id,
            'narration': narration,
            # considering partner's sale pricelist's currency
            # 'currency_id': self.pricelist_id.currency_id.id,
            'invoice_user_id': self.env.context.get('user_id', self.env.user.id),
            'invoice_date': self.date,
            # 'fiscal_position_id': self.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, invoice_line)],
            # 'invoice_cash_rounding_id': self.config_id.rounding_method.id
            # if self.config_id.cash_rounding and (not self.config_id.only_round_cash_method or any(p.payment_method_id.is_cash_count for p in self.payment_ids))
            # else False
        }
        new_move = self.env['account.move'].sudo().with_context(
            default_move_type=move_vals['move_type']).create(move_vals)
        #self.write({'account_move': new_move.id, 'state': 'invoiced'})
        self.write({'account_move': new_move.id})
        new_move.sudo()._post()

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
