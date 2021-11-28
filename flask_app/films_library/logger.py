import datetime
import logging
import os


def get_logging_mode(mode: str = None):
    """ Define logger mode based by environ variable $LOG_MODE """
    if mode is None:
        v_var = os.environ.get('LOG_MODE')
    else:
        v_var = mode

    if v_var == "DEBUG" or v_var is None:
        mode = logging.DEBUG
    elif v_var == "CRITICAL":
        mode = logging.CRITICAL
    elif v_var == "INFO":
        mode = logging.INFO
    elif v_var == "FATAL":
        mode = logging.FATAL
    elif v_var == "WARNING":
        mode = logging.WARNING
    elif v_var == "ERROR":
        mode = logging.ERROR
    return mode


class Logger:
    LOG_FILE_DEFAULT = "films_app.log"

    def __init__(self, file_path: str = None):
        if file_path is not None:
            self.file = file_path
        else:
            self.file = self.LOG_FILE_DEFAULT
        self.logger = logging.getLogger("Films_app")
        self.log_handler = logging.FileHandler(f"{self.file}", encoding='utf-8')
        self.logging_mode = get_logging_mode()
        print("logging mode:", self.logging_mode)
        self.log_handler.setLevel(self.logging_mode)
        self.logger.addHandler(self.log_handler)

    def change_level(self, mode: str):
        """ Changing logger mode.

        :param str mode: logger mode name. Can be 'ERROR', 'INFO', 'WARNING', 'DEBUG', 'FATAL'.

        :returns None

        :raise ValueError if mode argument unsopprted
        """
        if mode not in ('ERROR', 'INFO', 'WARNING', 'DEBUG', 'FATAL'):
            raise ValueError("Wring logger mode name. Must be 'ERROR', 'INFO', 'WARNING', 'DEBUG' or 'FATAL'.")
        logging.basicConfig(level=get_logging_mode(mode))

    @property
    def event_time(self):
        """ Property method, returns time then called as YYYY.MM.DD

        :returns: str
        """
        time = datetime.datetime.now()
        return datetime.datetime.strftime(time, "%Y.%m.%d-%H:%M")

    def debug(self, message: str):
        """ Debug implementation for custom logger

        :param str message: log text

        :returns: None
        """
        self.logger.debug(f"[{self.event_time}] -  {message}")

    def error(self, message: str):
        """ Error implementation for custom logger

        :param str message: log text

        :returns: None
        """
        self.logger.error(f"[{self.event_time}] -  {message}")

    def info(self, message: str):
        """ Info implementation for custom logger
        :param str message: log text

        :returns: None
        """
        self.logger.info(f"[{self.event_time}] -  {message}")

    def warning(self, message: str):
        """ Info implementation for custom logger
        :param str message: log text

        :returns: None
        """
        self.logger.warning(f"[{self.event_time}] -  {message}")

    def fatal(self, message: str):
        """ Info implementation for custom logger
        :param str message: log text

        :returns: None
        """
        self.logger.fatal(f"[{self.event_time}] -  {message}")


logging.basicConfig(level=get_logging_mode())
Log = Logger()
