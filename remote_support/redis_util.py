from django.conf import settings
from django.contrib.auth import get_user_model
import redis

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def getUserBySessionId(request):
    if not 'session_id' in request.COOKIES:
        return None
    session_id = request.COOKIES['session_id']
    email = session_storage.get(session_id)
    if not email:
        return None
    email = email.decode('utf-8')
    try:
        return get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        return None