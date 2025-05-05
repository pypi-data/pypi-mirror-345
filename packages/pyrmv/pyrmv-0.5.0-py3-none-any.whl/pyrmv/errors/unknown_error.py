class UnknownError(Exception):
    """Exception raised but error is not known.

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
