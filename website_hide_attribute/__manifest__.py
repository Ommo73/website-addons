{
    "name": """Checkboxes to hide attribute and sliders setting""",
    "summary": """Checkboxes to hide attribute and sliders setting""",
    "category": "eCommerce",
    # "live_test_url": "http://apps.it-projects.info/shop/product/website-multi-company?version=11.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Artem Rafailov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/iledarn",
    "license": "LGPL-3",
    # "price": 19.00,
    "currency": "EUR",

    "depends": [
        "theme_clarico",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/product_template_view.xml',
        'views/product_attribute_view.xml',
        'data/ir_filters.xml',
        'data/slider.xml',
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
