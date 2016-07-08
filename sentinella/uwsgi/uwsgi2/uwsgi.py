import json
import logging

import trollius as asyncio
from trollius import From

logger = logging.getLogger(__name__)


@asyncio.coroutine
def get_uwsgi_stats(agent):
    yield From(agent.run_event.wait())
    config = agent.config['uwsgi']
    logger.info('starting "get_uwsgi_stats" task for "%s"', config['hostname'])
    db_config = config['database']
    yield From(agent.async_create_database(**db_config))
    workers_stats = None
    uwsgi_host = config['hostname']
    uwsgi_port = config['port']
    while agent.run_event.is_set():
        yield From(asyncio.sleep(config['frequency']))
        try:
            logger.debug('open connection to uwsgi stats server')
            reader, writer = yield From(asyncio.open_connection(uwsgi_host,
                                                                uwsgi_port))
            data = yield From(reader.read())
            d = json.loads(data.decode('utf-8'))
            if workers_stats is None:
                logger.debug('first run, no previous statistics in memory')
                workers_stats = dict()
                for worker in d['workers']:
                    workers_stats[worker['id']] = worker
                logger.debug('current statistcs: %s', workers_stats)
                continue
            ref_worker = d['workers'][0]
            stored_last_spawn = workers_stats[ref_worker['id']]['last_spawn']
            received_last_spawn = ref_worker['last_spawn']
            if stored_last_spawn != received_last_spawn:
                logger.warn('a restart of the uwsgi server "%s" '
                            'has been detected',
                            uwsgi_host)
                workers_stats = dict()
                for worker in d['workers']:
                    workers_stats[worker['id']] = worker
                continue
            points = []
            for worker in d['workers']:
                logger.debug('process worker data...')
                stored_wk_data = workers_stats[worker['id']]
                requests = worker['requests'] - stored_wk_data['requests']
                exceptions = worker['exceptions'] - \
                    stored_wk_data['exceptions']
                tx = worker['tx'] - stored_wk_data['tx']
                points.append({
                    'measurement': 'uwsgi_stats',
                    'tags': {
                        'host': config['hostname'],
                        'worker': worker['id']
                    },
                    'fields': {
                        'requests': requests,
                        'exceptions': exceptions,
                        'tx': tx,
                        'rss': worker['rss'],
                        'vsz': worker['vsz'],
                        'avg_rt': worker['avg_rt'],
                        'wid': worker['id'],
                        'status': worker['status']
                    }
                })
                workers_stats[worker['id']] = worker
            yield From(agent.async_push(points, db_config['name']))
        except:
            logger.exception('cannot get the uwsgi stats')
    logger.info('get_uwsgi_stats terminated')
