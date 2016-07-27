import sys

PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

if PY34_PLUS:
    from .libvirt.libvirt import get_libvirt_stats
else:
    from .sentinella_libvirt.sentinella_libvirt import get_libvirt_stats
