import json
import logging
import os

import trollius as asyncio
from trollius import From
from libvirtmon import get_stats
logger = logging.getLogger(__name__)

frequency = 60
hostname = os.uname()[1].split('.')[0]

@asyncio.coroutine
def get_libvirt_stats(agent):
    yield From(agent.run_event.wait())
    #config = agent.config['libvirt']
    logger.info('starting "get_libvirt_stats" task for "%s"', hostname)

    while agent.run_event.is_set():
        yield From(asyncio.sleep(frequency))
        try:
            stats = get_stats()
            logger.debug('connecting to libvirt')
            for uuid, instance in stats.items():
                data['measurements'].append({'name': 'libvirt.instance',
                                         'tags': {'uuid': instance['uuid']},
                                         'value': instance['name']})

            
            logger.debug('{}: libvirt={}%'.format(hostname, data))
            yield From(agent.async_push(data))
        except:
            logger.exception('cannot get the libvirt information')

    logger.info('get_libvirt_stats terminated')
