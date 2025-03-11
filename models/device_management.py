from odoo import models, fields, api
import secrets


class DeviceManagement(models.Model):
    _name = 'device.management'
    _description = 'Device Management'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Device Name', required=True)
    device_identifier = fields.Char(string='Device Identifier', required=True)
    api_token = fields.Char(string='API Token', readonly=True, copy=False)
    is_active = fields.Boolean(string='Active', default=True)
    last_access = fields.Datetime(string='Last Access', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_device_identifier',
         'unique(device_identifier)',
         'Device Identifier must be unique!')
    ]

    @api.model
    def generate_token(self):
        return secrets.token_urlsafe(32)

    @api.model
    def create(self, vals):
        vals['api_token'] = self.generate_token()
        return super(DeviceManagement, self).create(vals)

    def regenerate_token(self):
        for record in self:
            record.api_token = self.generate_token()
        return True

    def validate_token(self, token):
        device = self.search([
            ('api_token', '=', token),
            ('is_active', '=', True)
        ], limit=1)
        if device:
            device.write({'last_access': fields.Datetime.now()})
            return device
        return False
