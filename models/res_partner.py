from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    golf_player = fields.Boolean("Is a golf player")
    golf_license = fields.Integer(
        string='golf license',
    )
    golf_handicap = fields.Integer(
        string='handicap',
    )
    
    golf_membership = fields.Many2one(
        string='Membership',
        comodel_name='product.template',
        ondelete='restrict',
    )

    