

class GEAIException(Exception):
    """Base class for all PyGEAI exceptions."""
    pass


class UnknownArgumentError(GEAIException):
    """Argument provided is not valid"""
    pass


class MissingRequirementException(GEAIException):
    """Requirement not available"""
    pass


class WrongArgumentError(GEAIException):
    """Wrongly formatted arguments"""
    pass


class ServerResponseError(GEAIException):
    """There was an error in the request to the server"""
    pass


class APIError(GEAIException):
    """There was an error in the request to the server"""
    pass




