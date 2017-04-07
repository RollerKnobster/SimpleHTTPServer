import logging

LOG_FORMAT = '%(asctime)s %(levelname)-10s %(name)-30s %(funcName)-30s \
<%(lineno)-3d> %(message)s'
logger = logging.getLogger()

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(LOG_FORMAT, datefmt="%H:%M:%S")
handler.setFormatter(formatter)

logger.addHandler(handler)
