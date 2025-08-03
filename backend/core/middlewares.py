from rest_framework_simplejwt.tokens import AccessToken
from django.utils.deprecation import MiddlewareMixin
from core.settings import logger

class UserContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        authorization_header = request.headers.get('Authorization')

        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            try:
                access_token = AccessToken(token)
                payload = access_token.payload
                user_id = payload.get('user_id')
                branch_id = payload.get('branch_id')
                role = payload.get('role')
                # Set the user context in the request
                request.user = {
                    'id': user_id,
                    'branch_id': branch_id,
                    'role': role    
                }
                logger.info("User context set: %s", request.user)
            except Exception as e:
                # Handle invalid token or missing claims
                pass

        return None