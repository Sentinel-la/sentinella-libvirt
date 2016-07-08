import sys
from setuptools import setup, find_packages


PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

exclude = ['sentinella.libvirt.libvirt2'
           if PY34_PLUS else 'sentinella.libvirt.libvirt']

install_requires = []

if not PY34_PLUS:
    install_requires.append('trollius==2.0')


setup(
    name='sentinella-libvirt',
    description='sentinella-libvirt is a Sentinel.la plugin that can collect metrics from libvirt.',
    version='0.5',
    packages=find_packages(exclude=exclude),
    zip_safe=False,
    namespace_packages=['sentinella'],
    install_requires=install_requires,
    author='The Sentinel.la Team',
    author_email='francisco@sentinel.la',
    url='https://github.com/Sentinel-la/sentinella-libvirt',
    license='ASF',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Monitoring',
    ],
    keywords='monitoring metrics agent openstack nova libvirt',
)
