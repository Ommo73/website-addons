# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.tools.float_utils import float_round
from odoo.http import request
from odoo.exceptions import UserError

from .. import azul


_logger = logging.getLogger(__name__)


class PaymentAcquirerAzul(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('azul', 'Azul')])
    azul_test_auth1 = fields.Char(string='Test Auth1', help='First authentication factor for the test environment.')
    azul_test_auth2 = fields.Char(string='Test Auth2', help='Second authentication factor for the test environment.')
    azul_prod_auth1 = fields.Char(string='Production Auth1',
                                  help='First authentication factor for the production environment.')
    azul_prod_auth2 = fields.Char(string='Production Auth2',
                                  help='Second authentication factor for the production environment.')
    azul_payment_channel = fields.Char(string='Payment Channel')
    azul_store = fields.Char(string="Merchant Identification Number (MID)")
    azul_input_mode = fields.Char(string="Input Mode")

    @api.onchange('provider', 'payment_flow')
    def _onchange_azul_paument_flow(self):
        if self.provider == 'azul' and self.payment_flow == 'form':
            self.payment_flow = 's2s'
            raise UserError(_("Pay via Payment Page doesn't work for Azul"))

    @api.multi
    def _azul_process_datavault(self, data):

        res = self._azul_call(azul.DATAVAULT_PROCESS, data)

        if res.get('ISOCode') != azul.SUCCESS_STATUS:
            raise exceptions.UserError("Method DataVault doesn't work. Wrong credentials?\n%s", res.get('ErrorDescription'))
        return res

    @api.multi
    def _azul_process_transaction(self, data):
        data.update({
            'PosInpuMode': self.azul_input_mode,
            'TrxType': 'Sales',
            'AcquirerRefData': 1
        })
        res = self._azul_call(azul.TRANSACTION_PROCESS, data)

        if res.get('ISOCode') != azul.SUCCESS_STATUS:
            raise exceptions.UserError("Method Process Transaction doesn't work. Wrong credentials?\n%s", res.get('ErrorDescription'))
        return res

    @api.multi
    def _azul_call(self, operation, params):
        # TODO: auth OLOLO CHEK HERE auth1 auth2 tut verificirujuca
        params.update({
            'Channel': self.azul_payment_channel,
            'Store': self.azul_store
        })
        sandbox = self.environment != 'prod'
        # send soup zapros nuzhno chtob bylo ponyatno ot kakogo prodavca zapros
        return azul.call(operation, params, sandbox=sandbox)

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirerAzul, self)._get_feature_support()
        res['tokenize'].append('azul')
        return res

    @api.model
    def azul_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'cc_number': data['cc_number'],
            'cc_holder_name': data['cc_holder_name'],
            'cc_expiry': data['cc_expiry'],
            'cc_brand': data['cc_brand'],
            'cc_cvc': data['cc_cvc'],
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id'])
        })
        return payment_token

    @api.multi
    def azul_s2s_form_validate(self, data):
        self.ensure_one()
        # mandatory fields
        for field_name in ["cc_number", "cc_cvc", "cc_holder_name", "cc_expiry", "cc_brand"]:
            if not data.get(field_name):
                return False
        if data['cc_expiry']:
            cc_expiry = [i.strip() for i in data['cc_expiry'].split('/')]
            if len(cc_expiry) != 2 or any(not i.isdigit() for i in cc_expiry):
                return False
            try:
                if datetime.now().strftime('%y%m') > datetime.strptime('/'.join(cc_expiry), '%m/%y').strftime('%y%m'):
                    return False
            except ValueError:
                return False
        return True


class PaymentTransactionAzul(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def azul_s2s_do_transaction(self, **kwargs):
        self.ensure_one()
        order = request.website.sale_get_order()

        transaction_params = {
            'Amount': int(float_round(order.amount_total * 100, 2)),
            'ITBIS': int(float_round(order.amount_tax * 100, 2)),
            'CurrencyPosCode': self._currency2azul_code(order.currency_id),
            'Payment': 1,
            'Plan': 0,
            'CustomerServicePhone': self.partner_phone,
            'OrderNumber': order.id,
            'CustomOrderID': order.partner_id.id,
            'DataVaultToken': self.payment_token_id.acquirer_ref,
            'SaveToDataVault': 1
        }
        result = self.acquirer_id._azul_process_transaction(transaction_params)
        return self._azul_s2s_validate_tree(result)

    @api.multi
    def _azul_s2s_validate_tree(self, tree):
        self.ensure_one()
        if self.state not in ('draft', 'pending', 'refunding'):
            _logger.info('Stripe: trying to validate an already validated tx (ref %s)', self.reference)
            return True
        # TODO: check all and change


        status = tree.get('ISOCode')
        if status == 'succeeded':
            new_state = 'refunded' if self.state == 'refunding' else 'done'
            self.write({
                'state': new_state,
                'date_validate': fields.datetime.now(),
                'acquirer_reference': tree.get('id'),
            })
            self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        else:
            error = tree['error']['message']
            _logger.warn(error)
            self.sudo().write({
                'state': 'error',
                'state_message': error,
                'acquirer_reference': tree.get('id'),
                'date_validate': fields.datetime.now(),
            })
            return False

    @api.model
    def _currency2azul_code(self, currency):
        code = currency.name
        assert code in azul.SUPPORTED_CURRENCY
        return code


class PaymentTokenAzul(models.Model):
    _inherit = 'payment.token'

    @api.model
    def azul_create(self, values):
        # TODO: CHECK IT!
        token = values.get('azul_token')
        payment_acquirer = self.env['payment.acquirer'].browse(values.get('acquirer_id'))
        # create token in the Data vault of Azul service
        if values.get('cc_number'):
            cc_expiry = [i.strip() for i in values['cc_expiry'].split('/')]
            payment_params = {
                'CardNumber': values['cc_number'].replace(' ', ''),
                'Expiration': datetime.strptime('/'.join(cc_expiry), '%m/%y').strftime('%Y%m'),
                'CVC': values['cc_cvc'],
                'TrxType': 'CREATE',
            }
            token = payment_acquirer._azul_process_datavault(payment_params)
            description = 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name'])
        else:
            partner_id = self.env['res.partner'].browse(values['partner_id'])
            description = 'Partner: %s (id: %s)' % (partner_id.name, partner_id.id)


        if not token:
            raise Exception('Azul DataVault: No token provided!')
        # TODO: check it HERE WE GET TOKEN MAKE WDB DEBUG STOP HERE HER
        values.update({
            'acquirer_ref': token.get('DataVaultToken'),
            'name': description
        })

        # TODO:we need to use token['DataVaultToken']
        # pop credit card info to info sent to create
        for field_name in ["cc_number", "cc_cvc", "cc_holder_name", "cc_expiry", "cc_brand", "azul_token"]:
            values.pop(field_name, None)
        return values
