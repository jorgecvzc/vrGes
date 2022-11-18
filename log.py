import logging

APP_LOGGER_NAME = 'VRGes'

def ini_logger(logger_name = APP_LOGGER_NAME, file_name=None, level=0):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    #logger.setLevel(0)
    
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


def get_logger(module_name):
    return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)