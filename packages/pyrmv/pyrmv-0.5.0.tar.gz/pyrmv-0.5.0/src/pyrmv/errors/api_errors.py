class ApiAuthError(Exception):
    """
    Access denied for accessId provided.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class ApiQuotaError(Exception):
    """
    Quota exceeded for accessId provided.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class ApiTooManyRequests(Exception):
    """
    Too many requests.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__


class ApiParamError(Exception):
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


class ApiFormatError(Exception):
    """
    Response format not supported.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__
