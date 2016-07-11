import sys

PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

if PY34_PLUS:
    from .libvirt.libvirt import get_libvirt_stats
else:
    from .libvirt2.uwsgi import get_libvirt_stats
