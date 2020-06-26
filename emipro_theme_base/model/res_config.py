from odoo import fields, models

class res_config(models.TransientModel):
    _inherit = "res.config.settings"

    facebook_sharing = fields.Boolean(string='Facebook', related='website_id.facebook_sharing',readonly=False)
    twitter_sharing = fields.Boolean(string='Twitter', related='website_id.twitter_sharing',readonly=False)
    linkedin_sharing = fields.Boolean(string='Linkedin', related='website_id.linkedin_sharing',readonly=False)
    mail_sharing = fields.Boolean(string='Mail', related='website_id.mail_sharing',readonly=False)

