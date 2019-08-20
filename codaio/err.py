class CodaError(Exception):
    pass


class NoApiKey(CodaError):
    pass


class DocumentNotFound(CodaError):
    pass


class InvalidFilter(CodaError):
    pass
