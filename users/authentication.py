import redis
import uuid
from django.conf import settings
from django.http import JsonResponse
from functools import wraps

# Connect to Redis
redis_client = redis.StrictRedis.from_url(settings.CACHES["default"]["LOCATION"], decode_responses=True)

def generate_session(user_id):
    """Generates a session ID and stores it in Redis"""
    session_id = str(uuid.uuid4())  # Generate unique session ID
    redis_client.setex(f"session:{session_id}", 86400, user_id)  # Store in Redis (expires in 24 hours)
    return session_id

def custom_login_required(view_func):
    """Custom authentication decorator to check Redis session"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        session_id = request.COOKIES.get("session_id")  # Retrieve session from cookies

        if not session_id or not redis_client.exists(f"session:{session_id}"):
            return JsonResponse({"error": "Authentication required"}, status=401)

        request.user_id = redis_client.get(f"session:{session_id}")  # Retrieve user ID
        return view_func(request, *args, **kwargs)

    return _wrapped_view
