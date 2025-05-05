class PsIncorrectParamError(Exception):
    """
    An invalid parameter combination was requested, i.e. the
    defined range of stable segments encompassed all public
    transport sections or it was attempted to search
    forward/backward from the end/beginning of the
    connection.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__
