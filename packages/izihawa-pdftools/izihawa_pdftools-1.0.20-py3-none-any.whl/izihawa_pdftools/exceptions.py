from izihawa_utils.exceptions import BaseError


class PdfProcessingError(BaseError):
    pass


class TooBigDifferenceAfterCompressionError(PdfProcessingError):
    pass


class EmptyTextError(PdfProcessingError):
    pass


class PyPdfError(PdfProcessingError):
    def __init__(self, nested_error):
        self.nested_error = nested_error
