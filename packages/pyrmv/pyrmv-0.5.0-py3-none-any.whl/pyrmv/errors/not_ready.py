class NotReadyYetError(Exception):
    """
    This method is not finished yet.
    """

    def __init__(self):
        super().__init__(self.__doc__)

    def __str__(self):
        return self.__doc__
