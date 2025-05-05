class SotAlreadyArrivedError(Exception):
    """
    Trip already arrived.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SotNotStartedError(Exception):
    """
    Trip not started.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SotCancelledError(Exception):
    """
    Trip cancelled.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SotAllTrainsFilteredError(Exception):
    """
    All trips filtered.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SotStayOnTripError(Exception):
    """
    No change. Stay on trip.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__
