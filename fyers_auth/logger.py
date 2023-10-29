import logging

class AuthLogger:
    def __init__(self, log_name = "AuthLogger", 
                 log_level=logging.INFO, 
                 log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
                 log_datefmt="%d-%b-%y %H:%M:%S", log_file=None, logging_on = False, **kwargs):
        self._logging_on = logging_on
        if not self._logging_on:
            return 
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(log_level)

        if log_file:
            handler = logging.FileHandler(log_file)
        else:
            handler = logging.StreamHandler()

        formatter = logging.Formatter(log_format, datefmt=log_datefmt)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_info(self, *args):
        if self._logging_on:
            for arg in args:
                self.logger.info(f" ✅ {arg} ")

    def log_error(self, *args):
        if self._logging_on:
            for arg in args:
                self.logger.error(f" ❌ {arg} ")

    def log_warning(self, *args):
        if self._logging_on:
            for arg in args:
                self.logger.warning(f" ❕ {arg} ")


