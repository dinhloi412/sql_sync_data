from odoo import models, fields, api
import pyodbc
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class SQLTableMapping(models.Model):
    _name = 'sql.table.mapping'
    _description = 'SQL Table to Odoo Model Mapping'

    name = fields.Char('Mapping Name', required=True)
    sql_table = fields.Char('SQL Table Name', required=True)
    odoo_model = fields.Char('Odoo Model', required=True)
    last_sync = fields.Datetime('Last Sync')
    date_field = fields.Char("Date field")
    sync_interval = fields.Selection([
        ('5', '5 Minutes'),
        ('15', '15 Minutes'),
        ('60', '1 Hour'),
    ], string='Sync Interval', default='15', required=True)
    active = fields.Boolean('Active', default=True)
    sync_config_id = fields.Many2one('sql.server.sync', string='Sync Configuration', required=True, ondelete='cascade')

    field_ids = fields.One2many('sql.field.mapping', 'mapping_id', string='Field Mappings')

class SQLFieldMapping(models.Model):
    _name = 'sql.field.mapping'
    _description = 'SQL Field to Odoo Field Mapping'

    mapping_id = fields.Many2one('sql.table.mapping', string='Table Mapping', required=True)
    sql_field = fields.Char('SQL Field Name', required=True)
    odoo_field = fields.Char('Odoo Field Name', required=True)
    is_key = fields.Boolean('Is Key Field', help='Use this field to check for existing records')

class SQLServerSync(models.Model):
    _name = 'sql.server.sync'
    _description = 'SQL Server Sync Configuration'

    name = fields.Char('Name', required=True)
    server = fields.Char('Server', required=True)
    database = fields.Char('Database', required=True)
    use_windows_auth = fields.Boolean('Use Windows Authentication', default=True)
    username = fields.Char('Username')
    password = fields.Char('Password')
    table_mapping_ids = fields.One2many('sql.table.mapping', 'sync_config_id', string='Table Mappings')

    def _get_sql_connection(self):
        try:
            if self.use_windows_auth:
                conn_string = (
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    'Trusted_Connection=yes;'
                )
            else:
                conn_string = (
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'UID={self.username};'
                    f'PWD={self.password}'
                )
            return pyodbc.connect(conn_string)
        except Exception as e:
            _logger.error(f"Connection error: {str(e)}")
            return False

    def sync_data(self, mapping=None):
        conn = self._get_sql_connection()
        if not conn:
            return False

        try:
            mappings = mapping and [mapping] or self.table_mapping_ids.filtered(lambda m: m.active)
            print(mappings, "mappings")
            for map_record in mappings:
                self._sync_table(conn, map_record)
            
            conn.close()
            return True
        except Exception as e:
            _logger.error(f"Sync error: {str(e)}")
            return False

    def _sync_table(self, conn, mapping):
        cursor = conn.cursor()
        
        # Build SQL query
        field_list = ', '.join([f.sql_field for f in mapping.field_ids])
        query = f"""
            SELECT {field_list} 
            FROM {mapping.sql_table}
        """
        if mapping.last_sync:
            query = query + f"""WHERE {mapping.date_field} > %s"""
            
        
        print(query, "query")
        if mapping.last_sync:
            cursor.execute(query, (mapping.last_sync,))
        else:
            cursor.execute(query)
            
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            record_dict = dict(zip(columns, row))
            print(record_dict, "record_dict")
            # Prepare Odoo record data
            odoo_vals = {}
            key_fields = {}
            
            for field_map in mapping.field_ids:
                value = record_dict.get(field_map.sql_field)
                odoo_vals[field_map.odoo_field] = value
                if field_map.is_key:
                    key_fields[field_map.odoo_field] = value
            
            # Create or update record in Odoo
            if key_fields:
                existing_record = self.env[mapping.odoo_model].search(
                    [(k, '=', v) for k, v in key_fields.items()], limit=1
                )
                if existing_record:
                    existing_record.write(odoo_vals)
                else:
                    self.env[mapping.odoo_model].create(odoo_vals)
            else:
                print("here")
                self.env[mapping.odoo_model].create(odoo_vals)
        
        mapping.last_sync = fields.Datetime.now()

    @api.model
    def _run_scheduled_sync(self):
        current_minute = datetime.now().minute
        
        # Get all active sync configurations
        sync_configs = self.search([])
        for config in sync_configs:
            # Fix: Use table_mapping_ids instead of mapping_ids
            for mapping in config.table_mapping_ids.filtered(lambda m: m.active):
                interval = int(mapping.sync_interval)
                
                # Check if it's time to sync based on the interval
                if current_minute % interval == 0:
                    config.with_context(scheduled=True).sync_data(mapping)