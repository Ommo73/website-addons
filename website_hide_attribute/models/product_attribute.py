
from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    common = fields.Boolean(string="Общий", default=False)
