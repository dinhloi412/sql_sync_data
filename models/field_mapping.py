from odoo import models, fields


class SQLFieldMapping(models.Model):
    _name = 'sql.field.mapping'
    _description = 'SQL Field to Odoo Field Mapping'

    mapping_id = fields.Many2one('sql.table.mapping', string='Table Mapping', required=True)
    sql_field = fields.Char('SQL Field Name', required=True)
    odoo_field = fields.Char('Odoo Field Name', required=True)
    is_key = fields.Boolean('Is Key Field', help='Use this field to check for existing records')

