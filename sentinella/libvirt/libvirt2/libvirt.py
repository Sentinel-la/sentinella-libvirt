import json
import logging

import trollius as asyncio
from trollius import From

logger = logging.getLogger(__name__)

frequency = 60
hostname = os.uname()[1].split('.')[0]

@asyncio.coroutine
def get_libvirt_stats(agent):
    yield From(agent.run_event.wait())
    config = agent.config['libvirt']
    logger.info('starting "get_libvirt_stats" task for "%s"', hostname)

    while agent.run_event.is_set():
        yield From(asyncio.sleep(frequency))
        try:
            data = {'server_name': hostname,
                    'measurements': []}
            logger.debug('connecting to libvirt')
            
            # [START] To be completed with libvirt code
            '''
            Example:
            
            instance = ''
            value = ''
            data['measurements'].append({'name': 'libvirt.cpu',
                                         'tags': {'instance': instance},
                                         'value': value})
                                         
            data['measurements'].append({'name': 'libvirt.mem',
                                         'tags': {'instance': instance},
                                         'value': value})
                                         
            data['measurements'].append({'name': 'libvirt.iops',
                                         'tags': {'instance': instance},
                                         'value': value})

            '''
            # [END] To be completed with libvirt code
            
            logger.debug('{}: libvirt={}%'.format(hostname, data))
            yield From(agent.async_push(data))
        except:
            logger.exception('cannot get the libvirt information')

    logger.info('get_libvirt_stats terminated')
