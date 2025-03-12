from odoo import api, fields, models, tools, SUPERUSER_ID


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
        try:
            cr = self.env.cr
            check_query = """
                SELECT id FROM weightman 
                WHERE ticket_num = %s
            """
            cr.execute(check_query, (values.get('Ticketnum'),))
            existing_record = cr.fetchone()
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
                cr.execute(update_query, params)

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
                cr.execute(insert_query, params)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
