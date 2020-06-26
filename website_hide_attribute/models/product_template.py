
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_product = fields.Boolean(string="Товары со скидкой", default=False)
    popular_product = fields.Boolean(string="Популярные товары", default=False)
    new_product = fields.Boolean(string="Новинки", default=False)
