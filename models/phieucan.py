from odoo import api, fields, models, tools, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class SyncWeightman(models.Model):
    _name = "sync.weightman"
    _description = "Đồng bộ phiếu cân"

    @staticmethod
    def _prepare_values(values):
        return (
            values.get('agent_name'),
            values.get('Docnum'),
            values.get('Truckno'),
            values.get('Prodname'),
            values.get('Custname'),
            values.get('Datein'),
            values.get('Dateout'),
            values.get('Firstweight'),
            values.get('Secondweight'),
            values.get('Netweight'),
            values.get('Note'),
            values.get('Trantype'),
            values.get('Prodcode'),
            values.get('Custcode'),
            values.get('time_in'),
            values.get('time_out'),
            values.get('date_time'),
            values.get('sobao'),
            values.get('tlbao'),
            values.get('tlbi'),
            values.get('tlthucte'),
            values.get('status')
        )

    @api.model
    def api_create_record(self, values):
        if not values.get('Ticketnum') or not values.get('agent_name'):
            return {
                'success': False,
                'error': "Thiếu Ticketnum"
            }

        savepoint_name = "sync_weightman_save"
        try:
            self.env.cr.execute("SAVEPOINT %s" % savepoint_name)
            self.env.cr.execute("""
                SELECT id FROM weightman 
                WHERE ticket_num = %s
            """, (values.get('Ticketnum'),))

            existing_record = self.env.cr.fetchone()
            common_values = self._prepare_values(values)

            if existing_record:
                update_query = """
                    UPDATE weightman SET
                        warehouse_id = %s,
                        docnum = %s,
                        truckno = %s,
                        prodname = %s,
                        custname = %s,
                        date_in = %s,
                        date_out = %s,
                        firstweight = %s,
                        secondweight = %s,
                        netweight = %s,
                        note = %s,
                        trantype = %s,
                        prodcode = %s,
                        custcode = %s,
                        time_in = %s,
                        time_out = %s,
                        date_time = %s,
                        sobao = %s,
                        tlbao = %s,
                        tlbi = %s,
                        tlthucte = %s,
                        status = %s,
                        write_date = NOW()
                    WHERE ticket_num = %s
                    RETURNING id
                """
                params = common_values + (values.get('Ticketnum'),)
                self.env.cr.execute(update_query, params)
                updated_id = self.env.cr.fetchone()

                self.env.cr.execute("RELEASE SAVEPOINT %s" % savepoint_name)

                return {
                    'success': True,
                    'message': f"Đã cập nhật bản ghi {values.get('Ticketnum')}",
                    'id': updated_id[0] if updated_id else existing_record[0]
                }
            else:
                insert_query = """
                    INSERT INTO weightman (
                        create_uid, create_date, write_uid, write_date, 
                        ticket_num, warehouse_id, docnum, truckno, prodname, custname,
                        date_in, date_out, firstweight, secondweight,
                        netweight, note, trantype, prodcode, custcode,
                        time_in, time_out, date_time, sobao, tlbao,
                        tlbi, tlthucte, status, active, sequence
                    ) VALUES (
                        %s, NOW(), %s, NOW(), %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, true, 10
                    )
                    RETURNING id
                """
                params = (SUPERUSER_ID, SUPERUSER_ID, values.get('Ticketnum')) + common_values
                self.env.cr.execute(insert_query, params)

                self.env.cr.execute("RELEASE SAVEPOINT %s" % savepoint_name)

                return {
                    'success': True,
                }

        except Exception as e:
            _logger.exception(f"Lỗi khi xử lý bản ghi: {str(e)}")
            self.env.cr.execute("ROLLBACK TO SAVEPOINT %s" % savepoint_name)
            return {
                'success': False,
                'error': str(e)
            }
