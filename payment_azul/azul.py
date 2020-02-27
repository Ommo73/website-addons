# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging
import json
from odoo.exceptions import UserError
from odoo import _
from requests import Session
from odoo.http import request


_logger = logging.getLogger(__name__)


try:
    from zeep import Client
    from zeep.transports import Transport
except ImportError as err:
    Client = None
    _logger.debug(err)

SUCCESS_STATUS = "00"

SUPPORTED_CURRENCY = [
    'USD',
    'EUR',
    'DOP',
]

# operation list
DATAVAULT_PROCESS = "ProcessDataVault"
TRANSACTION_PROCESS = "ProcessPayment"

ALTERNATIVE_PROD_URL = "https://contpagos.azul.com.do/Webservices/SOAP/default.asmx"

SANDBOX2WSDL_URL = {
    True: "https://pruebas.azul.com.do/webservices/SOAP/Default.asmx",
    False: "https://pagos.azul.com.do/webservices/SOAP/Default.asmx",
    "URL": ALTERNATIVE_PROD_URL
}

sandbox2client = {}


def get_client(sandbox=True):
    """Returns cached client or creates new one"""
    global client
    client = sandbox2client.get(sandbox)
    if not client:
        url = SANDBOX2WSDL_URL[sandbox]
        session = Session()
        # certificate_path = request.env['ir.config_parameter'].sudo().get_param('payment_azul.certificate_path')
        # session.verify = certificate_path
        session.verify = False
        # remove transport when certificate ia added
        transport = Transport(session=session)
        client = Client(url, transport=transport)
        sandbox2client[sandbox] = client
    return client


def call(operation, params=None, sandbox=True):
    params['format_return'] = 'json'
    _logger.debug('Call "%s" in sandbox=%s with args:\n%s', operation, sandbox, params)
    try:
        client = get_client(sandbox)
        operation = getattr(client.service, operation)
        params = params or {}
        response = operation(**params)
    except Exception as e:
        # if we cannot to connect to production url we need to use alternative production url
        if sandbox is False:
            return call(operation, params, sandbox="URL")
        raise UserError(_("Method %s doesn't work. Wrong credentials?\n%s" % (operation, e)))

    _logger.debug('Raw response:\n%s', response)
    res_json = json.loads(response)
    return res_json
