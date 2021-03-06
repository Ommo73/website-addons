{
    "name": """Sign-up event attendees to portal""",
    "summary": """Attendees can use portal dashboard to make extra purchases for the event, for example.""",
    "category": "Marketing",
    # "live_test_url": "http://apps.it-projects.info/shop/product/portal-event-tickets?version=10.0",
    "images": ["images/banner.jpg"],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "AGPL-3",
    "price": 190.00,
    "currency": "EUR",

    "depends": [
        "event",
        "partner_event",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/event_event_views.xml",
        "data/mail_template_data.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": False,
}
