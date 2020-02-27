# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from odoo.exceptions import ValidationError
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import re


_logger = logging.getLogger(__name__)


class AzulController(WebsiteSale):

    @http.route(['/payment/azul/s2s/create_json_3ds'], type='json', auth='public', csrf=False)
    def stripe_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        azul_card = request.env['azul.card']
        kwargs['cc_expiry'] = kwargs['cc_expiry'][:2] + ' / ' + kwargs['cc_expiry'][-2:]
        if 'remember_me' in kwargs and kwargs['remember_me']:
            new_card = dict((k, kwargs[k]) for k in ('cc_number', 'cc_holder_name', 'cc_expiry', 'cc_cvc') if k in kwargs)
            new_card['card_holder_user_id'] = request.env.user.id
            azul_card.create(new_card)
        if 'card_id' in kwargs and kwargs['card_id']:
            card = azul_card.browse(int(kwargs['card_id']))

            kwargs['cc_number'] = card.card_number
            kwargs['cc_holder_name'] = card.card_holder_name
            kwargs['cc_expiry'] = card.card_expiration_date
            kwargs['cc_cvc'] = card.card_cvc

        for k in ('cc_number', 'cc_holder_name', 'cc_expiry', 'cc_cvc'):
            if k not in kwargs or not kwargs[k]:
                message = 'Error: ' + k + ' field is absent'
                return {
                    'error': message
                }

        kwargs['CVC'] = kwargs['cc_cvc']
        kwargs['Expiration'] = '20' + kwargs['cc_expiry'][-2:] + kwargs['cc_expiry'][:2]
        kwargs['CardNumber'] = kwargs['cc_number']

        token = False
        acquirer = request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id')))

        try:
            if not kwargs.get('partner_id'):
                kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
            token = acquirer.s2s_process(kwargs)
        except ValidationError as e:
            message = e.args[0]
            if isinstance(message, dict) and 'missing_fields' in message:
                msg = _("The transaction cannot be processed because some contact details are missing or invalid: ")
                message = msg + ', '.join(message['missing_fields']) + '. '
                if request.env.user._is_public():
                    message += _("Please sign in to complete your profile.")
                    # update message if portal mode = b2b
                    if request.env['ir.config_parameter'].sudo().get_param('auth_signup.allow_uninvited', 'False').lower() == 'false':
                        message += _("If you don't have any account, please ask your salesperson to update your profile. ")
                else:
                    message += _("Please complete your profile. ")

            return {
                'error': message
            }

        # import wdb
        # wdb.set_trace()

        if not token:
            res = {
                'result': False,
            }
            return res

        res = {
            'result': True,
            'id': token.id,
            'short_name': token.short_name,
            '3d_secure': False,
            'verified': True,
        }
        return res

    @http.route(['/payment_azul/card_data'], type='json', auth='public')
    def get_card_data(self, **kwargs):
        result = {
            'data': False,
        }
        user_id = request.session.uid

        if not user_id:
            return result

        user = request.env['res.users'].browse(user_id)
        result['user_email'] = user.email
        cards = request.env['azul.card'].search_read([('card_holder_user_id', '=', user_id)],
                                                     ['id', 'card_number', 'card_holder_name', 'card_expiration_date']) or []
        for card in cards:
            card['card_number'] = re.sub('\d', '*', card['card_number'][:-4]) + card['card_number'][-4:]
        result['cards'] = cards
        result['company'] = user.company_id.name or ''
        result['order'] = request.env['sale.order'].browse(request.session.sale_order_id).display_name or ''

        return result
