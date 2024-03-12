import sys
import logging
from com.dtmilano.android.adb.adbclient import Timer
from roktracker.utils.console import console
from roktracker.utils.gui import ConfirmDialog, InfoDialog
from threading import ExceptHookArgs


class ConsoleExceptionHander:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle_exception(self, exc_type, exc_value, exc_traceback):
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
        self.handle_exception(exc.exc_type, exc.exc_value, exc.exc_traceback)


class GuiExceptionHandler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # needed because of how adb library is implemented...
        if issubclass(exc_type, Timer.TimeoutException):
            return

        self.logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        InfoDialog(
            "Error",
            "An error occured, see the log file for more info.\nYou probably have to restart this application.",
            "300x140",
        )

    def handle_thread_exception(self, exc: ExceptHookArgs):
        self.handle_exception(exc.exc_type, exc.exc_value, exc.exc_traceback)
