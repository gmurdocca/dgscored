from django.core.cache import cache

def cache_per(ttl=None, prefix=None, cache_post=False, username=None):
    def decorator(function):
        def apply_cache(request, *args, **kwargs):
            if not username:
                if request.user.is_anonymous():
                    user = 'anonymous'
                else:
                    user = request.user.id
            else:
                user = username

            if prefix:
                CACHE_KEY = '%s_%s'%(prefix, user)
            else:
                CACHE_KEY = 'view_cache_%s_%s'%(function.__name__, user)       

            if not cache_post and request.method == 'POST':
                can_cache = False
                response = None
            else:
                can_cache = True
                response = cache.get(CACHE_KEY, None)

            if not response:
                response = function(request, *args, **kwargs)
                if can_cache:
                    cache.set(CACHE_KEY, response, ttl)
            return response
        return apply_cache
    return decorator
