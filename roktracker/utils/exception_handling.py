import logging
import sys
from threading import ExceptHookArgs
from types import TracebackType

from com.dtmilano.android.adb.adbclient import (  # type: ignore no stub file is provided
    Timer,
)

from roktracker.utils.console import console


class ConsoleExceptionHander:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
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
            "A critical error occured and the program stopped. For more info view the log file."
        )

    def handle_thread_exception(self, exc: ExceptHookArgs):
        caught_exeption = exc.exc_value
        if caught_exeption is None:
            caught_exeption = BaseException("Unknown Thread Exception")

        self.handle_exception(exc.exc_type, caught_exeption, exc.exc_traceback)


class GuiExceptionHandler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
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
            "Error: An error occured, see the log file for more info.\nYou probably have to restart this application.",
        )

    def handle_thread_exception(self, exc: ExceptHookArgs):
        caught_exeption = exc.exc_value
        if caught_exeption is None:
            caught_exeption = BaseException("Unknown Thread Exception")

        self.handle_exception(exc.exc_type, caught_exeption, exc.exc_traceback)
