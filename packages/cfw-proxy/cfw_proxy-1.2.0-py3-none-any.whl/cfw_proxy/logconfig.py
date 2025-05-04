import logging
import colorlog

formatter = colorlog.ColoredFormatter(
    '%(log_color)s[%(levelname)-7s]%(reset)s %(thread)d %(name)s: %(message)s',
    log_colors={
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    },
    reset=True
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[handler])


def get_logger(name):
    return logging.getLogger(name)