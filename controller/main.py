from odoo import http
from odoo.http import request
import json
from .auth_middleware import validate_token


class WeightManAPIController(http.Controller):
    @http.route('/api/v1/weightmans', type='json', auth='none', methods=['POST'])
    @validate_token
    def create_record(self, **post):
        try:
            data = request.jsonrequest
            if not data and not data.get('data'):
                return {
                    'success': False,
                    'error': 'Invalid request data'
                }

            model = request.env['sync.weightman']
            print(model, "model")
            for item in data['data']:
                model.api_create_record(item)

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
        try:
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
