import io
import logging

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError, PdfStreamError
from pypdf.generic import DictionaryObject

from .exceptions import EmptyTextError, TooBigDifferenceAfterCompressionError
from .watermarks import base_pdf_processor, pdf_processors


def fix_pdf(data) -> bytes:
    from borb.pdf import PDF

    buffer_out = io.BytesIO()
    PDF.dumps(buffer_out, PDF.loads(data))
    buffer_out.flush()
    buffer_out.seek(0)
    return buffer_out.read()


def clean_metadata(pdf, doi=None):
    try:
        old_size = len(pdf)
        reader = PdfReader(io.BytesIO(pdf), strict=False)
        writer = PdfWriter()

        for d in writer._objects:
            d.pop("/Producer", None)
        writer._info = writer._add_object(DictionaryObject())

        pdf_processor = base_pdf_processor
        if doi:
            doi_prefix = doi.split("/")[0]
            if doi_prefix in pdf_processors:
                pdf_processor = pdf_processors[doi_prefix]
        pdf_processor.process(reader, writer, doi)
        if doi and doi.startswith("10."):
            writer.add_metadata({"/Doi": doi})
        buffer = io.BytesIO()
        writer.write_stream(buffer)
        buffer.flush()
        buffer.seek(0)

        data = buffer.read()
        new_size = len(data)

        if new_size / old_size < 0.8 or new_size / old_size > 1.1:
            print("Too big difference after compression", doi, old_size, new_size)
        if new_size / old_size > 1.50:
            raise TooBigDifferenceAfterCompressionError(
                old_size=old_size, new_size=new_size
            )
        if new_size < 2000:
            raise EmptyTextError()
        return data

    except (
        AttributeError,
        PdfReadError,
        PdfStreamError,
        UnicodeDecodeError,
        ValueError,
        UnboundLocalError,
    ):
        logging.getLogger("error").info("cannot clean")
        return pdf
