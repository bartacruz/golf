from odoo import models, fields, _, api

class GolfHole(models.Model):
    _name =  'golf.hole'
    _description =  'GolfHole'

    _rec_name = 'name'
    _order = 'number ASC'

    
    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )

    number = fields.Integer()
    par = fields.Integer()
    handicap = fields.Integer()
    
    field_id = fields.Many2one('golf.field', string='Field', required=True, ondelete='cascade', index=True, copy=False)

    length = fields.Integer(
        string=_('Length'),
    )

    
    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = str(vals.get("number")) or _("New")
        return super(GolfHole, self).create(vals)
    