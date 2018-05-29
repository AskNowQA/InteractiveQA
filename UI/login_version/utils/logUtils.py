import logging.config

def setup_logging(config):
    """
    Sets up the logging by reading location of the logging configuration from the config.
    """
    # this could be made relative/static instead of being read from a config file
    file_name = config['DEFAULT']['logConfig']
    logging.config.fileConfig(file_name)

def get_logger(name):
    """
    Returns a logger for the supplied module.
    """
    return logging.getLogger(name)
