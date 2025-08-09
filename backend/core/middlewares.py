from rest_framework_simplejwt.tokens import AccessToken
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)

class ResponseTimeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            if duration > 1.0:  # Log slow requests (>1 second)
                logger.warning(
                    "Slow API response: %s %s took %.2f seconds",
                    request.method,
                    request.path,
                    duration
                )
            elif hasattr(settings, 'DEBUG') and settings.DEBUG:
                logger.debug(
                    "API response: %s %s took %.3f seconds",
                    request.method,
                    request.path,
                    duration
                )
        return response

class UserContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Initialize with a default user context to avoid AttributeError
        default_user = type('User', (), {
            'id': None,
            'branch_id': 1,  # Default branch_id
            'role': 'guest',
            'is_authenticated': False
        })()
        
        authorization_header = request.headers.get('Authorization')

        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            try:
                access_token = AccessToken(token)
                payload = access_token.payload
                user_id = payload.get('user_id')
                branch_id = payload.get('branch_id', 1)  # Default to 1 if not found
                role = payload.get('role', 'user')
                
                # Set the user context in the request
                request.user = type('User', (), {
                    'id': user_id,
                    'branch_id': branch_id,
                    'role': role,
                    'is_authenticated': True
                })()
                
                # Only log in DEBUG mode to reduce overhead
                from django.conf import settings
                if settings.DEBUG:
                    logger.debug("User context set: ID=%s, Branch=%s, Role=%s", user_id, branch_id, role)
                    
            except Exception as e:
                # Handle invalid token or missing claims
                if hasattr(settings, 'DEBUG') and settings.DEBUG:
                    logger.warning("Token validation failed: %s", str(e))
                request.user = default_user
        else:
            # No authorization header, set default user
            request.user = default_user

        return None