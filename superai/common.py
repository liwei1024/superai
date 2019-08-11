import logging

import coloredlogs




def InitLog():
    coloredlogs.DEFAULT_FIELD_STYLES['filename'] = {'color': 'blue'}
    coloredlogs.DEFAULT_FIELD_STYLES['lineno'] = {'color': 'blue'}
    coloredlogs.DEFAULT_FIELD_STYLES['levelname'] = {'color': 'magenta'}
    fmt = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    datefmt = '%Y-%m-%d:%H:%M:%S'
    coloredlogs.install(fmt=fmt, datefmt=datefmt, level=logging.DEBUG)

