import logging

def get_logger(name: str):
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)
    return logging.getLogger(name)
