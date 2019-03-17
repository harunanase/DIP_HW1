"""
    This module is for dev-defined errors
"""



class Error(Exception):
    # Base class for error
    pass


class AppError(Error):
    def __init__(self, message):
        self.message = message
