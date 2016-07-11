import os
import asyncio
import json
import logging


logger = logging.getLogger(__name__)

frequency = 60
hostname = os.uname()[1].split('.')[0]


@asyncio.coroutine
def get_libvirt_stats(agent):
    # To be completed with Python 3 code

    logger.info('get_libvirt_stats terminated')
