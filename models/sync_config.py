from odoo import models, fields, api
import pyodbc
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


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
        print("sync_table")
        # Build SQL query
        field_list = ', '.join([f.sql_field for f in mapping.field_ids])
        query = f"""
                    SELECT {field_list} 
                    FROM {mapping.sql_table}
                """
        if mapping.last_sync and mapping.date_field:
            print(mapping.last_sync, "mapping.last_sync")
            # Use ? for SQL Server parameter placeholder (not %s which is for PostgreSQL)
            query = query + f" WHERE {mapping.date_field} > ?"
            print(query, "query")
            # Convert datetime to string in SQL Server format
            adjusted_time = mapping.last_sync + timedelta(hours=7)
            last_sync_str = adjusted_time.strftime('%Y-%m-%d %H:%M:%S')

            print(last_sync_str, "last_sync_str")
            cursor.execute(query, (last_sync_str,))  # Note the comma to make it a tuple
        else:
            cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            print(row, "row")
            record_dict = dict(zip(columns, row))
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
                print(odoo_vals, "odoo_vals-1s")
                existing_record = self.env[mapping.odoo_model].search(
                    [(k, '=', v) for k, v in key_fields.items()], limit=1
                )
                if existing_record:
                    print("update records")
                    existing_record.write(odoo_vals)
                else:
                    self.env[mapping.odoo_model].create(odoo_vals)
            else:
                print("here")
                self.env[mapping.odoo_model].create(odoo_vals)
        print("here")
        mapping.last_sync = fields.Datetime.now()

    @api.model
    def _run_scheduled_sync(self):
        print("_run_scheduled_sync")
        current_minute = datetime.now().minute

        # Get all active sync configurations
        sync_configs = self.search([])
        for config in sync_configs:
            for mapping in config.table_mapping_ids.filtered(lambda m: m.active):
                try:
                    config.with_context(scheduled=True).sync_data(mapping)
                except Exception as e:
                    _logger.error(f"Error in scheduled sync for mapping {mapping.name}: {str(e)}")
