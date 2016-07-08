import sys

PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

if PY34_PLUS:
    from .uwsgi.uwsgi import get_uwsgi_stats
else:
    from .uwsgi2.uwsgi import get_uwsgi_stats
