
from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale

import logging
_logger = logging.getLogger(__name__)


class WebsiteAttr(WebsiteSale):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        result = super(WebsiteAttr, self).shop(page, category, search, ppg, **post)
        if result.qcontext['pager']['page']['url'] == '/shop':
            result.qcontext['attributes'] = result.qcontext['attributes'].filtered(lambda p: p.common == True)
        return result
