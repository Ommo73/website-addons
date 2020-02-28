# -*- coding: utf-8 -*-
# Copyright 2017 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    # big timeout due to long redirects (checkout -> confirmation) in nobill cases
    def test_checkout_nobill_noship(self):
        self.phantom_js(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('shop_mandatory_fields_nobill_noship', 15000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.shop_mandatory_fields_nobill_noship.ready",
            login=None,
            timeout=220,
        )

    def test_checkout_bill_noship(self):
        self.phantom_js(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('shop_mandatory_fields_bill_noship', 3000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.shop_mandatory_fields_bill_noship.ready",
            login=None,
            timeout=170,
        )

    def test_checkout_bill_ship(self):
        self.phantom_js(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('shop_mandatory_fields_bill_ship', 3000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.shop_mandatory_fields_bill_ship.ready",
            login=None,
            timeout=200,
        )

    def test_checkout_nobill_ship(self):
        self.phantom_js(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('shop_mandatory_fields_nobill_ship', 15000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.shop_mandatory_fields_nobill_ship.ready",
            login=None,
            timeout=270,
        )
