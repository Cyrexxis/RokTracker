"""Custom exception classes for the rok tracker.

Defines AdbError and GovernorNotFoundError."""


class AdbError(RuntimeError):
    """An error with the ADB connection.

    Most likely the ADB server crashed or the connection timed out.
    """

    pass


class GovernorNotFoundError(RuntimeError):
    """No governor was found on the screen.

    Most likely cause is an inactive governor that can't be opened.
    """

    pass
