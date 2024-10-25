import logging


def setup_logging():
    """ Настройка логирования """
    logging.getLogger('sqlalchemy.engine.Engine').disabled = True
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')