# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, exceptions, _


class AzulCard(models.Model):
    _name = 'azul.card'

    card_number = fields.Char(string='Number')
    card_holder_name = fields.Char(string='Name')
    card_expiration_date = fields.Char(string='Expiration Date')
    card_cvc = fields.Integer(string='CVC')
    card_holder_user_id = fields.Many2one('res.users', 'User')
