"""Exception handling utilities for console and GUI runtimes."""

import logging
import sys
from threading import ExceptHookArgs
from types import TracebackType

from com.dtmilano.android.adb.adbclient import (  # type: ignore no stub file is provided
    Timer,
)

from roktracker.utils.console import console


class ConsoleExceptionHandler:
    """Handle exceptions when run in a console."""

    def __init__(self, logger: logging.Logger):
        """Creates an exception handler for a console application.

        Args:
            logger (logging.Logger): The logger to use
        """
        self.logger = logger

    def handle_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
        """Handles an exception.

        Args:
            exc_type (type[BaseException]): The exception type
            exc_value (BaseException): The exception value
            exc_traceback (TracebackType | None): The traceback if available
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # needed because of how adb library is implemented...
        if issubclass(exc_type, Timer.TimeoutException):
            # no sys excepthook to prevent error shown in the console
            return

        self.logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

        console.print(
            "A critical error occurred and the program stopped. For more info view the log file."
        )

    def handle_thread_exception(self, exc: ExceptHookArgs):
        """Handles exception that happened in another thread.

        Args:
            exc (ExceptHookArgs): The exception
        """
        caught_exception = exc.exc_value
        if caught_exception is None:
            caught_exception = BaseException("Unknown Thread Exception")

        self.handle_exception(exc.exc_type, caught_exception, exc.exc_traceback)


class GuiExceptionHandler:
    """Handle exceptions when run in a GUI."""

    def __init__(self, logger: logging.Logger):
        """Creates an exception handler for a console application.

        Args:
            logger (logging.Logger): The logger to use
        """
        self.logger = logger

    def handle_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
        """Handles an exception.

        Args:
            exc_type (type[BaseException]): The exception type
            exc_value (BaseException): The exception value
            exc_traceback (TracebackType | None): The traceback if available
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # needed because of how adb library is implemented...
        if issubclass(exc_type, Timer.TimeoutException):
            return

        self.logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        console.print(
            "Error: An error occurred, see the log file for more info.\nYou probably have to restart this application.",
        )

    def handle_thread_exception(self, exc: ExceptHookArgs):
        """Handles exception that happened in another thread.

        Args:
            exc (ExceptHookArgs): The exception
        """
        caught_exception = exc.exc_value
        if caught_exception is None:
            caught_exception = BaseException("Unknown Thread Exception")

        self.handle_exception(exc.exc_type, caught_exception, exc.exc_traceback)
