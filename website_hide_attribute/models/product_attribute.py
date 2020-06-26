# Copyright 2020 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    common = fields.Boolean(string="Общий", default=False)
