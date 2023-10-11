import logging
import os

logging.basicConfig(format='[%(levelname)s] %(name)s::%(lineno)d: %(funcName)s(): %(message)s')
logging.getLogger().setLevel(os.environ.get('LOGLEVEL', 'INFO'))
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
