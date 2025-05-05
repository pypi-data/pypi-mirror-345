import logging
import logging.config
import os


class LoggerConfig(logging.Logger):
    """
    A class to configure logging settings for an application.
    """

    def __init__(self, app_name, streams=('console', 'file'), file_name='NumWord.log'):
        """
        Initialize LoggerConfig with given parameters.

        Args:
            app_name (str): Name of the application.
            streams (tuple, optional): List of streams to log to. Options are ('file', ) or ('console', 'file') Default is ('console', ).
            file_name (str, optional): Name of the log file, default is 'SAM.log'.
        """
        super().__init__(app_name)
        self.__app_name = app_name
        self.__stream = list(streams)
        self.__filename = file_name

    def __handler_config(self):
        """
        Configure logging handlers based on the specified streams.

        Returns:
            dict: A dictionary containing the logging handler configurations.
                  Depending on the value of `self.__stream`, it can contain:

                  - Both 'console' and 'file' handlers
                  - Only 'file' handler
                  - Only 'console' handler

        Notes:
            - 'console': Logs will be displayed on the console.
            - 'file': Logs will be written to a file specified by `self.__filename`.

        """
        return {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': self.__filename,
                'formatter': 'default',
                'encoding': 'utf-8'
            }
        } if self.__stream == ['console', 'file'] else {
            'file': {
                'class': 'logging.FileHandler',
                'filename': self.__filename,
                'formatter': 'default',
                'encoding': 'utf-8'
            }
        } if self.__stream == ['file'] else {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            }
        }

    def __log_config(self):
        """
        Configure logging settings including formatters, handlers, and loggers.

        Constructs a dictionary containing the logging configuration details for the application.

        Returns:
            dict: Logging configuration dictionary with version, formatters, handlers, and loggers.

        """
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s'
                }
            },
            'handlers': self.__handler_config(),
            'loggers': {
                f'{self.__app_name}': {
                    'handlers': self.__stream,
                    'level': os.getenv('LOG_LEVEL', 'INFO'),
                    'propagate': True
                }
            }
        }

    def __configure_logger(self):
        """
        Configure the logger using the constructed logging configuration dictionary.

        Uses the `logging.config.dictConfig` method to apply the logging configuration.

        Returns:
            None: Configures the logger settings for the application.
        """
        if 'file' in self.__stream:
            log_dir = os.path.dirname(self.__filename)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

        logging.config.dictConfig(self.__log_config())

    def get_logger(self):
        """
        Retrieve the logger for the application.

        Returns:
            logging.Logger: Returns a logger instance configured for the application.
        """
        self.__configure_logger()
        return logging.getLogger(self.__app_name)
