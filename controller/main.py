from odoo import http
from odoo.http import request
import json
from .auth_middleware import validate_token


class WeightManAPIController(http.Controller):
    @http.route('/api/v1/weightmans', type='json', auth='none', methods=['POST'])
    @validate_token
    def create_record(self, **post):
        """
        API endpoint to create a new record
        Example request:
        {
            "name": "Test Record",
            "description": "This is a test record"
        }
        """
        try:
            data = request.jsonrequest
            if not data and not data.get('data'):
                return {
                    'success': False,
                    'error': 'Invalid request data'
                }
            model = request.env['weightman']
            for item in data['data']:
                result = model.api_create_record(item)

            return {
                'success': True,
                'message': "Record created successfully"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/v1/weightmans', type='http', auth='none', methods=['GET'])
    def get_records(self, **kwargs):
        """
        API endpoint to fetch records
        Optional query parameters: name, active
        """
        try:
            # domain = []
            # if kwargs.get('name'):
            #     domain.append(('name', 'ilike', kwargs['name']))
            # if kwargs.get('active'):
            #     domain.append(('active', '=', kwargs['active'] == 'true'))

            # model = request.env['custom.model']
            # result = model.api_get_records(domain)
            return request.make_response(
                json.dumps({
                    "data": "Hello World"}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')]
            )
