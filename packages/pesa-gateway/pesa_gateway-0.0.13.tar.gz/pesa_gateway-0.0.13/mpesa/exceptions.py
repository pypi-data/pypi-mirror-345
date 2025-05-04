class MpesaError(Exception):
    """Base exception for all MPesa errors"""

    pass


class MpesaAPIError(MpesaError):
    """Exception for errors returned by the MPesa API"""

    pass
