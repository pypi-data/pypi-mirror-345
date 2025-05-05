class SvcParamError(Exception):
    """Exception raised for errors in the input arguments.

    ### Attributes:
        * errorCode: Client error code from HAFAS ReST Request Errors.
        * errorText: Description of an error occurred.
    """

    def __init__(self, errorCode: str, errorText: str):
        self.errorCode = errorCode
        self.errorText = errorText
        super().__init__(self.errorText)

    def __str__(self):
        return f"{self.errorCode} -> {self.errorText}"


class SvcLocationError(Exception):
    """
    Location missing or invalid.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcLocationArrivalError(Exception):
    """
    Arrival location missing or invalid.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcLocationDepartureError(Exception):
    """
    Departure location missing or invalid.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcLocationViaError(Exception):
    """
    Unknown change stop.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcLocationEqualError(Exception):
    """
    Origin/destination or vias are equal.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcLocationNearError(Exception):
    """
    Origin and destination are too close.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcDatetimeError(Exception):
    """
    Date/time are missing or invalid.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcDatetimePeriodError(Exception):
    """
    Date/time are not in timetable or allowed period.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcProductError(Exception):
    """
    Product field missing or invalid.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcContextError(Exception):
    """
    Context is invalid.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcNoResultError(Exception):
    """
    No result found.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcSearchError(Exception):
    """
    Unsuccessful search.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class SvcNoMatchError(Exception):
    """
    No match found.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__
