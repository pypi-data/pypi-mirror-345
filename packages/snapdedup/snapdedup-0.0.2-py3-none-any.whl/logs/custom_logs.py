import logging
import logging.config
import os


class LoggerCfg(logging.Logger):
    """
    Configurable logging utility for console and file output.
    """

    def __init__(self, name, outputs=('console', 'file'), log_file='snap_dedup.log'):
        """
        Initialize the logger configuration.

        Args:
            name (str): Name of the logger.
            outputs (tuple, optional): Destinations for log output ('console', 'file', or both).
            log_file (str, optional): Filename for log output (if 'file' is specified) Default: snap_dedup.log.
        """
        super().__init__(name)
        self._name = name
        self._outputs = list(outputs)
        self._log_file = log_file

    def __define_handlers(self):
        """
        Create handler definitions based on specified outputs.

        Returns:
            dict: Mapping of handler names to handler configurations.
        """
        handlers = {}
        if 'console' in self._outputs:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        if 'file' in self._outputs:
            handlers['file'] = {
                'class': 'logging.FileHandler',
                'filename': self._log_file,
                'formatter': 'standard',
                'encoding': 'utf-8'
            }
        return handlers

    def __build_config(self):
        """
        Constructs the logging configuration.

        Returns:
            dict: A logging configuration dictionary.
        """
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
                }
            },
            'handlers': self.__define_handlers(),
            'loggers': {
                self._name: {
                    'handlers': self._outputs,
                    'level': os.getenv('LOG_LEVEL', 'INFO'),
                    'propagate': True
                }
            }
        }

    def __setup(self):
        """
        Apply the logging configuration using dictConfig.
        """
        if 'file' in self._outputs:
            directory = os.path.dirname(self._log_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
        logging.config.dictConfig(self.__build_config())

    def get_logger(self):
        """
        Returns the configured logger instance.

        Returns:
            logging.Logger: The logger associated with the configured name.
        """
        self.__setup()
        return logging.getLogger(self._name)
