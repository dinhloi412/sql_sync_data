from odoo import http
from odoo.http import request
import json
import logging
from .auth_middleware import validate_token

_logger = logging.getLogger(__name__)


class WeightManAPIController(http.Controller):
    @http.route('/api/v1/weightmans', type='json', auth='none', methods=['POST'])
    @validate_token
    def create_record(self, **post):
        try:
            data = request.jsonrequest
            if not data or not data.get('data'):
                return {
                    'success': False,
                    'error': 'Dữ liệu không hợp lệ'
                }

            try:
                model = request.env['sync.weightman'].sudo()
            except KeyError as ke:
                return {
                    'success': False,
                    'error': f"Not found model: {str(ke)}"
                }
            for item in data['data']:
                model.api_create_record(item)
            return {
                'success': True,
            }

        except Exception as e:
            _logger.exception(f"Lỗi trong API: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }