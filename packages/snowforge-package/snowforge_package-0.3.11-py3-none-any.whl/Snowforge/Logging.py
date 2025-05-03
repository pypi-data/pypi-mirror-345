import logging
from colored import Fore, Style

class Debug:
    """Handles logging with colored output for better visibility."""
    
    logger = logging.getLogger("SnowforgeLogger")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Ensure the logger only has one handler (avoid duplicate logs)
    if not logger.hasHandlers():
        logger.addHandler(handler)

    @staticmethod
    def log(message: str, level='INFO', verbose_logging: bool = False):
        """Logs a message with a specified severity level and colored output.

        Args:
            message (str): The message to log.
            level (str, optional): The log level (INFO, DEBUG, ERROR, etc.). Defaults to "INFO".
            verbose_logging (bool, optional): Set to True to enable DEBUG output globally. Defaults to False.
        """

        # Adjust log level based on verbose flag
        if verbose_logging:
            Debug.logger.setLevel(logging.DEBUG)
        else:
            Debug.logger.setLevel(logging.INFO)

        # Convert level to uppercase
        level = level.upper()

        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        # Define color mapping
        color_map = {
            'INFO': Fore.white,
            'ERROR': Fore.red,
            'DEBUG': Fore.blue,
            'WARNING': Fore.yellow,
            'SUCCESS': Fore.light_green,
            'FAILURE': Fore.red,
            'CRITICAL': Fore.light_red
        }

        colored_message = f"{color_map.get(level, Fore.white)}{message}{Style.reset}"

        # Ensure the log level exists
        if level in log_levels:
            getattr(Debug.logger, level.lower())(colored_message)
        else:
            Debug.logger.info(colored_message)
