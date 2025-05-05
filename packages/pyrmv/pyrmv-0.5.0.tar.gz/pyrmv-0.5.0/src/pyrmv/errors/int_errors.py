class IntError(Exception):
    """
    Internal RMV server error.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class IntGatewayError(Exception):
    """
    Communication error with RMV backend systems.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class IntTimeoutError(Exception):
    """
    Timeout during service processing.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__
