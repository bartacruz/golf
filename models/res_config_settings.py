# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _,fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    golf_club_id = fields.Char(config_parameter='golf.club_id')
    golf_default_product = fields.Many2one("product.product",string=_("Default product"), config_parameter='golf.default_product')
    golf_default_identification_type = fields.Many2one("l10n_latam.identification.type", config_parameter='golf.default_identification_type')
    golf_default_responsibility = fields.Many2one("l10n_ar.afip.responsibility.type", config_parameter='golf.default_responsibility')

    golf_default_field_18 = fields.Many2one("golf.field",string=_("Default field 18"), config_parameter='golf.default_field_18')
    golf_default_field_9 = fields.Many2one("golf.field",string=_("Default field 9"), config_parameter='golf.default_field_9')
    golf_members_pricelist = fields.Many2one('product.pricelist', config_parameter='golf.members_pricelist')
    
