from functools import wraps
from odoo.http import request
import json

def validate_token(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print("Validating token")
        auth_header = request.httprequest.headers.get('Authorization')
        print(auth_header, "auth_header")
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': 'Invalid or missing authorization token'
                }),
                headers=[('Content-Type', 'application/json')],
                status=401
            )
        
        token = auth_header.split(' ')[1]
        print(token, 'token')
        device_model = request.env['device.management'].sudo()
        device = device_model.validate_token(token)
        
        if not device:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': 'Invalid token'
                }),
                headers=[('Content-Type', 'application/json')],
                status=401
            )
        
        # Add device to the request context
        request.device = device
        return func(self, *args, **kwargs)
    
    return wrapper