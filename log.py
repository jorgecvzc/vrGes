import logging

LOGGER_APP_NAME = 'VRGes'
LOGGER_LEVEL = logging.DEBUG

def ini_logger(logger_name = LOGGER_APP_NAME, level=LOGGER_LEVEL, file_name=None):
    logger = logging.getLogger(logger_name)
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s')
    
    sh = logging.StreamHandler()    
    sh.setFormatter(formatter)
    
    logger.handlers.clear()
    logger.addHandler(sh)

    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def get_logger(module_name, logger_name=LOGGER_APP_NAME):
    return logging.getLogger(logger_name).getChild(module_name)