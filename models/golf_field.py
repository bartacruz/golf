from odoo import models, fields, _, api

class GolfField(models.Model):
    _name =  'golf.field'
    _description =  'a golf field'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    hole_ids = fields.One2many("golf.hole",'field_id', 'Holes')
    par = fields.Integer()
    length_blue = fields.Integer()
    length_white = fields.Integer()

    @api.onchange("hole_ids")
    def _calculate_data(self):
        self.par = sum(c.par for c in self.hole_ids)
        self.length_blue = sum(c.length_blue for c in self.hole_ids)
        self.length_white = sum(c.length_white for c in self.hole_ids)

    
