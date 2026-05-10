"""IP-based throttle for dedicated admin portal login."""

import logging

from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def _lockout_cache_key(ip: str) -> str:
    return f'admin_login_lockout:{ip}'


def _attempts_cache_key(ip: str) -> str:
    return f'admin_login_attempts:{ip}'


def is_admin_login_locked(ip: str) -> bool:
    return bool(cache.get(_lockout_cache_key(ip)))


def clear_admin_attempts(ip: str) -> None:
    cache.delete(_attempts_cache_key(ip))


def record_admin_failed_login(ip: str) -> None:
    limit = getattr(settings, 'ADMIN_LOGIN_ATTEMPT_LIMIT', 5)
    ttl = getattr(settings, 'ADMIN_LOGIN_LOCKOUT_DURATION', 900)

    ak = _attempts_cache_key(ip)
    attempts = cache.get(ak, 0) + 1
    cache.set(ak, attempts, ttl)

    if attempts >= limit:
        cache.set(_lockout_cache_key(ip), True, ttl)
        logger.warning('Admin portal lockout for IP %s after %s failed attempts', ip, attempts)


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or ''
