from odoo import models, fields


class SQLTableMapping(models.Model):
    _name = 'sql.table.mapping'
    _description = 'SQL Table to Odoo Model Mapping'

    name = fields.Char('Mapping Name', required=True)
    sql_table = fields.Char('SQL Table Name', required=True)
    odoo_model = fields.Char('Odoo Model', required=True)
    last_sync = fields.Datetime('Last Sync')
    date_field = fields.Char("Date field")
    active = fields.Boolean('Active', default=True)
    sync_config_id = fields.Many2one('sql.server.sync', string='Sync Configuration', required=True, ondelete='cascade')

    field_ids = fields.One2many('sql.field.mapping', 'mapping_id', string='Field Mappings')

