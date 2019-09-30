class CodaError(Exception):
    pass


class NoApiKey(CodaError):
    pass


class DocumentNotFound(CodaError):
    pass


class InvalidFilter(CodaError):
    pass


class NotFound(CodaError):
    pass


class TableNotFound(NotFound):
    pass


class RowNotFound(NotFound):
    pass


class ColumnNotFound(NotFound):
    pass


class AmbiguousName(CodaError):
    pass


class InvalidCell(CodaError):
    pass
