# Copyright 2020 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_product = fields.Boolean(string="Товары со скидкой", default=False)
    popular_product = fields.Boolean(string="Популярные товары", default=False)
    new_product = fields.Boolean(string="Новинки", default=False)
