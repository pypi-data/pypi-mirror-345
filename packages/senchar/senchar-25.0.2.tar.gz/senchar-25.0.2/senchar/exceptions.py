"""
Contains custom exceptions and warnings used throughout senchar.
"""

import senchar

import warnings

warnings.filterwarnings("ignore")


def warning(message: str) -> None:
    """
    Print and log a warning message.
    """

    # warnings.warn(message)
    # print(f"Warning: {message}")

    try:
        senchar.logger.warning(message)
    except Exception:
        print(f"Warning: {message}")

    return


class SencharError(Exception):
    """
    Base custom error class for azsencharam.
    """

    def __init__(self, message: str, error_code: int = 0):
        """
        Custom error exception for senchar.

        Usage:  raise senchar.exceptions.SencharError(message)

        Args:
          message: string message to display when error is raised
          error_code: flag for code, from list below
          - 0 - no error
        """

        super().__init__(message)

        self.error_code = 0

        # Now for your custom code...
        if error_code is not None:
            self.error_code = error_code
            # Original error was self.errors.message

        if senchar.logger.logger is not None:
            senchar.logger.error(message)
        else:
            print(f"SencharError: {message}")
