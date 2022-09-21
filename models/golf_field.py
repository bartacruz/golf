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
    
    external_reference = fields.Char(string = "External reference") # AAG ID
    tee_color = fields.Char(string=_("Tee color"))
    slope_rating_front = fields.Float(string=_("Slope Rating Front"),digits=(4,2))
    slope_rating_back = fields.Float(string=_("Slope Rating Back"),digits=(4,2))
    slope_rating_total = fields.Float(string=_("Slope Rating Total"),digits=(4,2))

    course_rating_front = fields.Float(string=_("Course Rating Front"),digits=(4,2))
    course_rating_back = fields.Float(string=_("Course Rating Back"),digits=(4,2))
    course_rating_total = fields.Float(string=_("Course Rating Total"),digits=(4,2))
    
    hole_ids = fields.One2many("golf.hole",'field_id', 'Holes')
    hole_count = fields.Integer(compute='_compute_hole_count')
    par = fields.Integer()
    length = fields.Integer()

    def _compute_hole_count(self):
        for record in self:
            record.hole_count = len(record.hole_ids)
            
    @api.onchange("hole_ids")
    def _calculate_data(self):
        self.par = sum(c.par for c in self.hole_ids)
        self.length = sum(c.length for c in self.hole_ids)
    