from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from odoo.http import request 
 
class website(models.Model):
    _inherit = "website"
   
    is_ajax_sorting_products = fields.Boolean(string="Load Products through Ajax")
    show_more_msg = fields.Char(string='Show More Message',translate=True,default="Show More")
    show_less_msg = fields.Char(string='Show Less Message',translate=True,default="Show Less")
    view_all_msg = fields.Char(string='View All Message',translate=True,default="View All")    
    is_price_filter_enable = fields.Boolean(string="Allow Price Filter")
    facebook_sharing = fields.Boolean(string='Facebook')
    twitter_sharing = fields.Boolean(string='Twitter')
    linkedin_sharing = fields.Boolean(string='Linkedin')
    mail_sharing = fields.Boolean(string='Mail')
	
    # to render main parent product.public.category website specific
    def category_check(self):
        return self.env['product.public.category'].sudo().search([('website_published','=',True),('parent_id', '=', False),('website_id', 'in', (False,self.id))])
    
    
    # to render full path for breadcrumbs based on argument
    # args : product.public.category
    # return : list of category path and website url
    def get_product_categs_path(self, id):
        categ_set = []
        if id:
            while id:
                categ = self.env['product.public.category'].sudo().search([('id', '=', id)])
                categ_set.append(categ.id)
                if categ and categ.parent_id:
                    id = categ.parent_id.id
                else:
                    break
            
        # For Reverse order
        categ_set = categ_set[::-1]
        
        values = {
            'categ_set': categ_set,
            'web_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        }
        return values
    
    #Return The Current Pricelist Item For diplay a Offer In Slider 
    def get_pricelist_item_id(self,product):
        item_ids= self.get_current_pricelist().item_ids
        for item in item_ids:
            if item.date_end and item.date_end >= datetime.today().date():
                if item.applied_on == '0_product_variant':
                    if product.product_variant_id[0].id == item.product_id.id:
                        return item
                elif item.applied_on == '1_product':
                    if product.id == item.product_tmpl_id.id:
                        return item
                elif item.applied_on == '2_product_category':
                    if product.categ_id.id == item.categ_id.id :
                        return item
                elif item.applied_on == '3_global': 
                    return item
        return False
    
    def get_recently_viewed_items(self, product_id=False):
        recently_viewed_product_ids = request.session.get('recently_viewed_product_ids', False)
        if not recently_viewed_product_ids and not product_id:
            return False

        # set product id into session if it not into session if session is not than create a session
        if product_id:
            if recently_viewed_product_ids:
                if product_id not in request.session['recently_viewed_product_ids']:
                    if len(recently_viewed_product_ids)>=10:
                        recently_viewed_product_ids.pop()
                    tmp = recently_viewed_product_ids
                    tmp.insert(0, product_id)
                    request.session['recently_viewed_product_ids'] = tmp
                else:
                    recently_viewed_product_ids.remove(product_id)
                    tmp = recently_viewed_product_ids
                    tmp.insert(0, product_id)
                    request.session['recently_viewed_product_ids'] = tmp

            else:
                request.session['recently_viewed_product_ids'] = [product_id]

        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(price, to_currency, request.env.user.company_id,fields.Date.today())
        values = {            
            'recent_products': request.session.get('recently_viewed_product_ids', False),     
            'compute_currency': compute_currency        
            } 
        return values

    # Get minimum price and maximum price according to Price list as well as discount for Shop page
    def get_min_max_prices(self):
        range_list = []
        cust_min_val = request.httprequest.values.get('min_val', False)
        cust_max_val = request.httprequest.values.get('max_val', False)

        products = self.env['product.template'].search(self.website_domain())
        prices_list = []
        if products:
            pricelist = self.get_current_pricelist()
            for prod in products:
                context = dict(self.env.context, quantity=1, pricelist=pricelist.id if pricelist else False)
                product_template = prod.with_context(context)

                list_price = product_template.price_compute('list_price')[product_template.id]
                price = product_template.price if pricelist else list_price
                if price:
                    prices_list.append(price)

        if not prices_list: return False

        if not cust_min_val and not cust_max_val:
            range_list.append(round(min(prices_list)))
            range_list.append(round(max(prices_list)))
            range_list.append(round(min(prices_list)))
            range_list.append(round(max(prices_list)))
        else:
            range_list.append(cust_min_val)
            range_list.append(cust_max_val)
            range_list.append(round(min(prices_list)))
            range_list.append(round(max(prices_list)))
        return range_list
