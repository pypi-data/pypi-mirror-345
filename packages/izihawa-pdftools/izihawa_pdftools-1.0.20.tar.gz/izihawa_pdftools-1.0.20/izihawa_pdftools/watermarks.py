import binascii
import logging
import re
from typing import cast

from pypdf._cmap import build_char_map, unknown_char_map
from pypdf.errors import PdfStreamError
from pypdf.generic import ContentStream, DictionaryObject, NameObject

from .text_collector import TextCollector

elsevier_regexp = re.compile(
    r"(Downloaded|Descargado) (for|para) .* (at|en) .* (from|de) .* "
    r"(by|por) .* (on|en) \w+ \d{1,2}, \d{4}\. "
    r"(For personal use only|Para uso personal exclusivamente)\. (No other uses without permission|No se permiten otros usos sin autorización)\. "
    r"Copyright ©\d{4}\. Elsevier Inc\. (All rights reserved|Todos los derechos reservados)\."
)
bmj_regexp = re.compile(
    r"^.*: first published as .* on \d{1,2} \w+ \d{4}\. Downloaded from .*"
    r" on \w+ \d{1,2}, \d{4} at .*\s*Protected by\s*copyright\."
)
doi1017_regexp = re.compile(
    r"(?:Downloaded from https?://.* by .* user on \d\d \w+ \d+)|"
    r"(?:(?:https?://doi\.org/10\.1017/(cbo|CBO)?[0-9.\-]+\s+)?"
    r"Published online by Cambridge University Press)"
)
doi1097_regexp = re.compile(r"Downloaded from https?://.* by .* on \d\d \w+ \d+")
precise_id_regexp = re.compile(
    r"Downloaded from http.* by .*\s?on\s?\d\d/\d\d/\d\d\d\d"
)
doi1212_regexp = re.compile(
    r"Copyright © .*\.\s*Unauthorized reproduction of this article is prohibited\."
    r"\s*Downloaded from https?://.* by .* on \d+/\d+/\d+$"
)
doi1213_regexp = re.compile(r"Downloaded from http://.* by [\w\-+=/]+ on \d+/\d+/\d+")
downloaded_regexp = re.compile(rb"^[Dd]ownloaded [Ff]rom:? https?://")
terms_of_use_regexp = re.compile(rb"^[Tt]erms [Oo]f [Uu]se:? https?://")
doi1542_regexp = re.compile(
    r"Downloaded from https?://(.*) by .+ user on \d{1,2} \w+ \d{4}"
)
doi4028_regexp = re.compile(
    r"All rights reserved\. No part of contents of this paper may be reproduced or transmitted "
    r"in any form or by any means without the written permission of .*\s*.*, www\.scientific\.net\.\s*"
    r"\(#\d+, .*-\s*\d+/\d+/\d+,\d+:\d+:\d+\)"
)
brill_regexp = re.compile(
    r"Downloaded from Brill\.com\s*\d\d/\d\d/\d\d\d\d \d\d:\d\d:\d\d(AM|PM)\s*(?:via\s*(?:\w+\s*){,7})?$"
)
doi23919_regexp = re.compile(
    r"Authorized licensed use limited to:\s*.*\.\s*Downloaded on \w+ \d+\s*,"
    r"\s*\d+ at \d+:\d+:\d+ .* from IEEE Xplore\.\s*Restrictions apply\."
)
manualslib_regexp = re.compile(
    r"Downloaded from www\.[mM]anualslib\.com manuals search engine"
)


def _is_downloaded_from_https_watermark(text):
    return bool(re.search(downloaded_regexp, text)) or bool(
        re.search(terms_of_use_regexp, text)
    )


def _is_1002_watermark(text: bytes) -> bool:
    return bool(
        re.search(
            rb"[dD]ownloaded from https?://(.*) by .+ on \[\d{1,2}/\d{1,2}/\d{4}]", text
        )
    )


def _is_1017_watermark(text: bytes) -> bool:
    return bool(re.search(doi1017_regexp, text))


def _is_1021_watermark(text: bytes) -> bool:
    return text.startswith(b"Downloaded via ") or text.startswith(
        b"See https://pubs.acs.org/sharingguidelines for options "
        b"on how to legitimately share published articles."
    )


def _is_1029_watermark(text):
    return bool(
        re.search(
            rb"^\s*\d+,\s*\d+\s*,\s*.,\sDownloaded from .* by .*, .* on \[\d\d/\d\d/\d\d\d\d\]\. See the Terms and Conditions .* on .*$",
            text,
        )
    )


def _is_1037_watermark(text):
    return (
        text
        == b"ThisdocumentiscopyrightedbytheAmericanPsychologicalAssociationoroneofitsalliedpublishers."
        or text
        == b"Thisarticleisintendedsolelyforthepersonaluseoftheindividualuserandisnottobedisseminatedbroadly."
    )


def _is_1038_watermark(text):
    return bool(
        re.search(rb"^.*Downloaded from .*$", text)
        or re.search(
            rb"Access provided by .* on \d\d/\d\d/\d\d\.\sFor personal use only\.", text
        )
    )


def _is_1039_watermark(text):
    return bool(
        re.search(
            rb"^Published on \d+ \w+ \d{2,4}\. Downloaded\s*(by .*)?\s*on \d+/\d+/\d+ \d+:\d+:\d+ (AM|PM)\.\s*$",
            text,
        )
    )


def _is_1055_watermark(text: str) -> bool:
    return bool(re.search(rb"^Downloaded by: .*\. Copyrighted material\.$", text))


def _is_1056_watermark(text: str) -> bool:
    return bool(
        re.search(
            rb"^Downloaded from nejm\.org( at .*)? on \w+ \d+,\s*\d\d\d\d\.\s*For personal use only\.\s*No other uses without permission\.\s*$",
            text,
        )
        or re.search(rb"^\s*The New England Journal of Medicine\s*$", text)
        or re.search(
            rb"^\s*Copyright \xc2\xa9 \d{2,4} .*\. All rights reserved\.\s*$", text
        )
    )


def _is_1061_watermark(text: str) -> bool:
    return bool(
        re.search(
            rb"^Downloaded from ascelibrary\.org by .* on \d\d/\d\d/\d\d\..*$", text
        )
    )


def _is_1063_watermark(text: str) -> bool:
    return bool(re.search(rb"\d\d? \w+ \d\d\d\d \d\d:\d\d:\d\d", text))


def _is_1079_watermark(text: str) -> bool:
    return bool(
        re.search(
            rb"(Downloaded from .* by \d+\.\d+\.\d+\.\d+, on [\d/]+\.)|"
            rb"(Subject to the CABI Digital Library Terms & Conditions, available at .*)",
            text,
        )
    )


def _is_1080_watermark(text: str) -> bool:
    return bool(
        re.search(rb"^Downloaded by .* at \d\d:\d\d \d\d \w+ \d\d\d\d.*$", text)
    )


def _is_1089_watermark(text: str) -> bool:
    return bool(re.search(rb"^Downloaded by .* from .* at \d\d/\d\d/\d\d\..*$", text))


def _is_1093_watermark(text: str) -> bool:
    return bool(
        re.search(rb"^Downloaded from https?://(.*) by .* on \d{1,2} \w+ \d{4}", text)
    )


def _is_1097_copyright(text: str) -> bool:
    return (
        b"\xa92020by" in text
        or b"Unauthorizedreproductionofthisarticleisprohibited." in text
        or b"PublishedbyWoltersKluwerHealth" in text
        or b"Unauthorized reproduction of this article is prohibited." in text
    )


def _is_1109_watermark(text):
    return bool(
        re.search(
            rb"^\s*Authorized licensed use limited to:.*\.\s*Downloaded on .* at \d+:\d+:\d+ UTC from .*\.\s*Restrictions apply\.\s*$",
            text,
        )
    )


def _is_1111_watermark(text: bytes):
    return bool(
        re.search(
            rb"^[\d\s,]+Downloaded from https?://(.*) by .*,\s*.* on \[\d{1,2}/\d{2}/\d{4}]\..*$",
            text,
        )
    )


def _is_1128_watermark(text: bytes):
    return bool(re.search(rb"Downloaded from https?://(.*) on .+ by .*", text))


def _is_1142_watermark(text: bytes):
    return bool(
        re.search(rb"^.*\s*Downloaded from .*$", text)
        or re.search(rb"^by .* on \d\d/\d\d/\d\d\..*$", text)
    )


def _is_1144_watermark(text: bytes):
    return bool(re.search(rb"^Downloaded from .* by .* on \w+ \d+,\s*\d+\.?$", text))


def _is_1146_watermark(text: bytes):
    return bool(
        re.search(rb"^\s*Annu\. Rev\. [\w\d\s\.]+\s?.*\s*Downloaded from .*\s*$", text)
        or re.search(
            rb"^\s*Access provided by .* on \d+/\d+/\d+\. For personal use only\.\s*$",
            text,
        )
    )


def _is_1152_watermark(text: bytes):
    return bool(re.search(rb"^Downloaded from .* at .* on \w+ \d+,\s*\d+\.?$", text))


def _is_1161_watermark(text: bytes):
    return bool(
        re.search(
            rb"^Downloaded from https?://ahajournals\.org by on \w+ \d+, \d+$", text
        )
    )


def _is_1200_watermark(text: bytes):
    return bool(
        re.search(
            rb"Downloaded from .* by .* on \w{1,5} \d+, \d{4} from \d+\.\d+\.\d+\.\d+\s*",
            text,
        )
        or re.search(rb"Copyright \xc2\xa9 \d{4} .*\.\s*All rights reserved\.\s*", text)
    )


def _is_1210_watermark(text: bytes):
    return bool(
        re.search(
            rb"Downloaded from .* by .* on \d+ \w{1,5} \d{4}",
            text,
        )
    )


def _is_1212_watermark(text: bytes):
    return bool(re.search(rb"Downloaded from https?://(.*) by .+ on .* \d{4}", text))


def _is_1287_watermark(text: bytes):
    return bool(
        re.search(rb"Downloaded from .* by .* on \d+.*\d+,\s*at\s*\d+:\d+.*$", text)
    )


def _is_1353_watermark(text: bytes):
    return bool(re.search(rb"^\[.*]\s+Project MUSE\s+\(.*\)\s*.*$", text))


def _is_1520_watermark(text):
    return b"8QLYHUVLW\\\x032I\x03:HVWHUQ" in text


def _is_1680_watermark(text):
    return bool(
        re.search(rb"^Downloaded by \[.*] on \[\d+/\d+/\d+]\.\s*Copyright.*$", text)
    )


def _is_2214_watermark(text):
    return bool(
        re.search(
            rb"^Downloaded from .* by .* on \d\d/\d\d/\d\d from IP address \d+\.\d+\.\d+\.\d+\. Copyright .*\. For personal use only; all rights reserved\s*$",
            text,
        )
    )


def _is_downloaded_from_with_digital_date(text: bytes):
    return bool(re.search(rb"^Downloaded from .* by .* on \d\d/\d\d/\d\d\d\d$", text))


def _is_downloaded_from_with_date(text: bytes):
    return bool(re.search(rb"^Downloaded from .* by .* on \d+ \w+ \d\d\d\d$", text))


def _is_2307_watermark(text):
    return bool(re.search(rb"\d\d? \w+ \d\d\d\d \d\d:\d\d:\d\d", text))


def _is_2514_watermark(text: bytes):
    return bool(
        re.search(rb"^\s*Downloaded by .* on .* | https?://.* | DOI:.*\s*$", text)
    )


def _is_7326_watermark(text: bytes):
    return bool(re.search(rb"^Downloaded from .* by .* on \d+/\d+/\d\d\d\d\.$", text))


def _is_7566_watermark(text: bytes):
    return bool(
        re.search(rb"^.*?\nDownloaded from .*? by .* on \s*\d+/\d+/\d+\s*$", text)
    )


def _is_17226_watermark(text: bytes):
    return bool(text == b"Copyright National Academy of Sciences. All rights reserved.")


class BasePageRemover:
    pass


class NoPageRemover(BasePageRemover):
    def should_remove(self, page_num, page):
        return False


class PageNumPageRemover(BasePageRemover):
    def __init__(self, page_nums):
        self.page_nums = set(page_nums)

    def should_remove(self, page_num, page):
        return page_num in self.page_nums


class ContentPageRemover(BasePageRemover):
    def __init__(self, page_nums, content_re):
        self.page_nums = set(page_nums)
        self.content_re = re.compile(content_re, flags=re.DOTALL)

    def should_remove(self, page_num, page):
        if page_num not in self.page_nums:
            return False
        text = page.extract_text()
        if self.content_re.search(text):
            return True
        return False


class BasePdfProcessor:
    def __init__(self, page_remover: BasePageRemover = None):
        self.page_remover = page_remover or NoPageRemover()

    def process_page(self, page, pdf_reader, page_num, doi):
        return False

    def process(self, pdf_reader, pdf_writer, doi):
        for page_num, page in enumerate(pdf_reader.pages):
            is_page_modified = False
            if self.page_remover.should_remove(page_num, page):
                continue
            try:
                is_page_modified = self.process_page(page, pdf_reader, page_num, doi)
            except (PdfStreamError, binascii.Error) as e:
                logging.getLogger("nexus_pylon").warning(
                    {
                        "action": "pdf_stream_error",
                        "mode": "pylon",
                        "error": str(e),
                    }
                )
            if page.get_contents() is None:
                continue
            pdf_writer.add_page(page)
            if is_page_modified:
                pdf_writer.pages[-1].compress_content_streams(level=9)


class BaseWatermarkEraser(BasePdfProcessor):
    def __init__(
        self,
        is_watermark_predicate=_is_downloaded_from_https_watermark,
        watermark_orientations=None,
        page_remover: BasePageRemover = None,
    ):
        super().__init__(page_remover=page_remover)
        self.is_watermark_predicate = is_watermark_predicate
        self.watermark_orientations = (
            watermark_orientations
            if watermark_orientations is not None
            else (0, 90, 180, 270)
        )


class WatermarkEraser1(BaseWatermarkEraser):
    def process_page(self, page, pdf_reader, page_num, doi):
        is_page_modified = False
        if "/XObject" in page["/Resources"]:
            xobj = page["/Resources"]["/XObject"]
            content = ContentStream(page.get_contents(), pdf_reader, "bytes")

            xobj_death_note = []
            operations_death_note = []
            for op_i, (operands, operation) in enumerate(content.operations):
                if operation == b"Do":
                    nested_op = xobj[operands[0]]
                    if nested_op and nested_op["/Subtype"] != "/Image":
                        text = page.extract_xform_text(
                            nested_op, self.watermark_orientations, 200.0
                        )  # type: ignore
                        if self.is_watermark_predicate(text.encode()):
                            xobj_death_note.append(operands[0])
                            operations_death_note.append(op_i)
                            logging.getLogger("nexus_pylon").debug(
                                {
                                    "action": "watermark_removal",
                                    "mode": "pylon",
                                    "text": text,
                                }
                            )

            # Erase dictionary objects with watermarks
            for op_i in sorted(xobj_death_note, reverse=True):
                del xobj[op_i]

            # Erase operations with watermarks
            for op_i in reversed(operations_death_note):
                del content.operations[op_i]

            if operations_death_note or xobj_death_note:
                page.__setitem__(NameObject("/Contents"), content)
                is_page_modified = True

        return is_page_modified


class WatermarkEraser2(BaseWatermarkEraser):
    def process_page(self, page, pdf_reader, page_num, doi):
        is_page_modified = False
        content = ContentStream(page.get_contents(), pdf_reader, "bytes")
        operations_death_note = []
        for op_i, (operands, operation) in enumerate(content.operations):
            if operation == b"Tj":
                if isinstance(operands[0], bytes) and self.is_watermark_predicate(
                    operands[0]
                ):
                    operations_death_note.append(op_i)
                    logging.getLogger("nexus_pylon").debug(
                        {
                            "action": "watermark_removal",
                            "mode": "pylon",
                            "text": operands[0].decode(),
                        }
                    )

        # Erase operations with watermarks
        for op_i in reversed(operations_death_note):
            del content.operations[op_i]

        if operations_death_note:
            page.__setitem__(NameObject("/Contents"), content)
            is_page_modified = True

        return is_page_modified


class WatermarkEraser3(BaseWatermarkEraser):
    def process_page(self, page, pdf_reader, page_num, doi):
        is_page_modified = False
        content = ContentStream(page.get_contents(), pdf_reader, "bytes")
        operations_death_note = []

        for op_i, (operands, operation) in enumerate(content.operations):
            if operation == b"TJ":
                text = b""
                for operand in operands[0]:
                    if isinstance(operand, bytes):
                        text += operand
                if self.is_watermark_predicate(text):
                    operations_death_note.append(op_i)
                    logging.getLogger("nexus_pylon").debug(
                        {
                            "action": "watermark_removal",
                            "mode": "pylon",
                            "text": str(text),
                        }
                    )

        # Erase operations with watermarks
        for op_i in reversed(operations_death_note):
            del content.operations[op_i]

        if operations_death_note:
            page.__setitem__(NameObject("/Contents"), content)
            is_page_modified = True

        return is_page_modified


class WatermarkEraser4(BaseWatermarkEraser):
    def __init__(
        self, regexp, inverted=False, separator="", page_remover: BasePageRemover = None
    ):
        super().__init__(page_remover=page_remover)
        self.regexp = regexp
        self.inverted = inverted
        self.separator = separator

    def process_page(self, page, pdf_reader, page_num, doi):
        is_page_modified = False
        content = ContentStream(page.get_contents(), pdf_reader, "bytes")
        operations_death_note = []

        cmaps = {}
        space_width = 200.0
        if "/Resources" in page:
            resources_dict = cast(DictionaryObject, page["/Resources"])
        else:
            resources_dict = DictionaryObject()
        tc = TextCollector(self.inverted, self.separator)

        if "/Font" in resources_dict:
            for f in cast(DictionaryObject, resources_dict["/Font"]):
                cmaps[f] = build_char_map(f, space_width, page)

        cm_stack = []
        cmap = ("charmap", {}, "NotInitialized")
        start_trial = False
        matched = None
        text = None

        for op_i, (operands, operation) in enumerate(content.operations):
            if operation == b"q":
                cm_stack.append(cmap)
            elif operation == b"Q":
                try:
                    cmap = cm_stack.pop()
                except Exception:
                    pass
            elif operation == b"Tf":
                try:
                    cmap = (
                        cmaps[operands[0]][2],
                        cmaps[operands[0]][3],
                        operands[0],
                    )
                except KeyError:  # font not found
                    cmap = (
                        unknown_char_map[2],
                        unknown_char_map[3],
                        "???" + operands[0],
                    )
            elif operation == b"Tj":
                if isinstance(operands[0], str):
                    text = operands[0]
                else:
                    if isinstance(cmap[0], str):
                        try:
                            t = operands[0].decode(cmap[0], "surrogatepass")
                        except Exception:
                            t = operands[0].decode(
                                "utf-16-be" if cmap[0] == "charmap" else "charmap",
                                "surrogatepass",
                            )
                    else:
                        t = "".join(
                            [
                                cmap[0][x] if x in cmap[0] else bytes((x,)).decode()
                                for x in operands[0]
                            ]
                        )
                    text = "".join([cmap[1][x] if x in cmap[1] else x for x in t])
                tc.add_piece(text, op_i)
                text, matched = tc.match(self.regexp)
                if matched:
                    start_trial = True
                else:
                    if start_trial:
                        operations_death_note.extend(matched)
                        logging.getLogger("nexus_pylon").debug(
                            {
                                "action": "watermark_removal",
                                "mode": "pylon",
                                "matched": text,
                            }
                        )
                        tc.clear()
                        start_trial = False

        if start_trial:
            operations_death_note.extend(matched)
            logging.getLogger("nexus_pylon").debug(
                {
                    "action": "watermark_removal",
                    "mode": "pylon",
                    "matched": text,
                }
            )
            tc.clear()

        # Erase operations with watermarks
        for op_i in reversed(operations_death_note):
            del content.operations[op_i]

        if operations_death_note:
            page.__setitem__(NameObject("/Contents"), content)
            is_page_modified = True

        return is_page_modified


class WatermarkComposer(BaseWatermarkEraser):
    def __init__(self, watermark_erasers):
        super().__init__()
        self.watermark_erasers = watermark_erasers

    def process_page(self, page, pdf_reader, page_num, doi):
        is_page_modified = False
        for we in self.watermark_erasers:
            is_page_modified_new = we.process_page(page, pdf_reader, page_num, doi)
            is_page_modified = is_page_modified or is_page_modified_new
        return is_page_modified


class WatermarkConditionalWrapper(BaseWatermarkEraser):
    def __init__(self, regexp, nested_watermark_eraser):
        super().__init__()
        self.regexp = regexp
        self.nested_watermark_eraser = nested_watermark_eraser

    def process_page(self, page, pdf_reader, page_num, doi):
        is_page_modified = False
        if self.regexp.match(doi):
            is_page_modified = self.nested_watermark_eraser.process_page(
                page, pdf_reader, page_num, doi
            )
        return is_page_modified


pdf_processors = {
    "manualslib": WatermarkEraser4(manualslib_regexp, separator=""),
    "10.1001": WatermarkEraser2(
        is_watermark_predicate=_is_downloaded_from_with_digital_date,
        watermark_orientations=(0,),
    ),
    "10.1002": WatermarkEraser1(
        is_watermark_predicate=_is_1002_watermark, watermark_orientations=(270,)
    ),
    "10.1016": WatermarkComposer(
        [
            WatermarkEraser4(elsevier_regexp),
            WatermarkConditionalWrapper(
                regexp=re.compile(r"^10\.1016/j\.amsu\..*$"),
                nested_watermark_eraser=WatermarkEraser4(
                    regexp=re.compile(
                        r"Downloaded from http.* by .* on \d\d/\d\d/\d\d\d\d"
                    )
                ),
            ),
        ]
    ),
    "10.1017": WatermarkEraser4(doi1017_regexp, separator=" "),
    "10.1021": WatermarkEraser1(
        is_watermark_predicate=_is_1021_watermark, watermark_orientations=(90,)
    ),
    "10.1029": WatermarkEraser1(
        is_watermark_predicate=_is_1029_watermark, watermark_orientations=(270,)
    ),
    "10.1037": WatermarkEraser3(
        is_watermark_predicate=_is_1037_watermark,
        watermark_orientations=(0, 90, 270, 180),
    ),
    "10.1038": WatermarkEraser1(
        is_watermark_predicate=_is_1038_watermark, watermark_orientations=(90,)
    ),
    "10.1039": WatermarkEraser1(
        is_watermark_predicate=_is_1039_watermark, watermark_orientations=(0,)
    ),
    "10.1055": WatermarkEraser2(
        is_watermark_predicate=_is_1055_watermark, watermark_orientations=(90,)
    ),
    "10.1056": WatermarkEraser1(
        is_watermark_predicate=_is_1056_watermark, watermark_orientations=(0,)
    ),
    "10.1061": WatermarkEraser1(
        is_watermark_predicate=_is_1061_watermark, watermark_orientations=(90,)
    ),
    "10.1063": WatermarkEraser2(
        is_watermark_predicate=_is_1063_watermark,
        page_remover=ContentPageRemover(
            (0,), r"Articles Y\s?o\s?u May Be Interested In"
        ),
    ),
    "10.1073": WatermarkEraser1(watermark_orientations=(90,)),
    "10.1079": WatermarkEraser1(
        is_watermark_predicate=_is_1079_watermark, watermark_orientations=(0,)
    ),
    "10.1080": WatermarkEraser1(
        is_watermark_predicate=_is_1080_watermark,
        page_remover=ContentPageRemover(
            (0,),
            r"(^This article was downloaded by:.*|To cite this article:.*To link to this article:.*)",
        ),
    ),
    "10.1088": WatermarkEraser1(
        is_watermark_predicate=lambda text: False,
        page_remover=ContentPageRemover(
            (0,),
            r"You may also like.*This content was downloaded from IP address|This article has been downloaded from IOP\s?science.\s?Please scroll down to see the full text article\.",
        ),
    ),
    "10.1089": WatermarkEraser1(
        is_watermark_predicate=_is_1089_watermark, watermark_orientations=(90,)
    ),
    "10.1093": WatermarkEraser2(
        is_watermark_predicate=_is_1093_watermark, watermark_orientations=(270,)
    ),
    "10.1097": WatermarkComposer(
        [
            WatermarkEraser3(
                is_watermark_predicate=_is_1097_copyright, watermark_orientations=(0,)
            ),
            WatermarkEraser4(regexp=precise_id_regexp, separator=""),
            WatermarkEraser4(regexp=doi1097_regexp, separator=""),
        ]
    ),
    "10.1109": WatermarkEraser2(is_watermark_predicate=_is_1109_watermark),
    "10.1111": WatermarkEraser1(
        is_watermark_predicate=_is_1111_watermark, watermark_orientations=(270,)
    ),
    "10.1115": WatermarkEraser2(
        is_watermark_predicate=_is_downloaded_from_with_date,
        watermark_orientations=(270,),
    ),
    "10.1116": WatermarkEraser1(
        is_watermark_predicate=lambda text: False,
        page_remover=ContentPageRemover((0,), r"Articles you may be interested in"),
    ),
    "10.1126": WatermarkEraser1(watermark_orientations=(270,)),
    "10.1128": WatermarkEraser1(
        is_watermark_predicate=_is_1128_watermark, watermark_orientations=(90,)
    ),
    "10.1136": WatermarkEraser4(bmj_regexp, inverted=True),
    "10.1142": WatermarkEraser1(
        is_watermark_predicate=_is_1142_watermark, watermark_orientations=(90,)
    ),
    "10.1144": WatermarkEraser1(
        is_watermark_predicate=_is_1144_watermark, watermark_orientations=(0,)
    ),
    "10.1146": WatermarkEraser1(
        is_watermark_predicate=_is_1146_watermark, watermark_orientations=(90, 270)
    ),
    "10.1149": WatermarkEraser1(
        is_watermark_predicate=lambda text: False,
        page_remover=ContentPageRemover(
            page_nums=(0,),
            content_re=r"To cite this article:.*This content was downloaded from IP address .* on .* at .*",
        ),
    ),
    "10.1152": WatermarkEraser1(
        is_watermark_predicate=_is_1152_watermark, watermark_orientations=(0,)
    ),
    "10.1158": WatermarkEraser2(is_watermark_predicate=_is_downloaded_from_with_date),
    "10.1161": WatermarkEraser1(
        is_watermark_predicate=_is_1161_watermark, watermark_orientations=(270,)
    ),
    "10.1163": WatermarkEraser4(brill_regexp, separator=" "),
    "10.1200": WatermarkEraser1(
        is_watermark_predicate=_is_1200_watermark, watermark_orientations=(0,)
    ),
    "10.1210": WatermarkEraser2(
        is_watermark_predicate=_is_1210_watermark, watermark_orientations=(270,)
    ),
    "10.1212": WatermarkComposer(
        [
            WatermarkEraser1(_is_1212_watermark, watermark_orientations=(90,)),
            WatermarkEraser4(doi1212_regexp, separator=""),
        ]
    ),
    "10.1213": WatermarkEraser4(doi1213_regexp),
    "10.1215": WatermarkEraser4(doi1542_regexp, separator=" "),
    "10.1287": WatermarkEraser1(
        is_watermark_predicate=_is_1287_watermark,
        watermark_orientations=(90,),
        page_remover=ContentPageRemover((0,), r"^This article was downloaded by:.*"),
    ),  # redl
    "10.1353": WatermarkEraser2(
        is_watermark_predicate=_is_1353_watermark,
        watermark_orientations=(90,),
    ),
    "10.1519": WatermarkEraser4(precise_id_regexp, separator=" "),  # regex is correct
    "10.1520": WatermarkEraser1(
        is_watermark_predicate=_is_1520_watermark, watermark_orientations=(0,)
    ),
    "10.1525": WatermarkEraser2(
        is_watermark_predicate=_is_downloaded_from_with_date,
        watermark_orientations=(90, 270),
    ),
    "10.1542": WatermarkEraser4(doi1542_regexp, separator=" "),
    "10.1680": WatermarkEraser1(
        is_watermark_predicate=_is_1680_watermark, watermark_orientations=(0,)
    ),
    "10.1681": WatermarkEraser4(
        precise_id_regexp,
        page_remover=ContentPageRemover(
            (0,), r"Articles Y\s?o\s?u May Be Interested In"
        ),
    ),
    "10.2106": WatermarkEraser4(precise_id_regexp),
    "10.2108": WatermarkEraser3(),
    "10.2214": WatermarkEraser1(
        _is_2214_watermark, watermark_orientations=(90, 270)
    ),  # regex is correct
    "10.2215": WatermarkEraser4(precise_id_regexp, separator=" "),  # regex is correct
    "10.2307": WatermarkEraser2(
        is_watermark_predicate=_is_2307_watermark,
        page_remover=ContentPageRemover(
            (0,),
            r"Your use of the JSTOR archive indicates your acceptance of the Terms & Conditions",
        ),
    ),
    "10.2337": WatermarkEraser2(
        is_watermark_predicate=_is_downloaded_from_with_date,
        watermark_orientations=(90,),
    ),
    "10.2514": WatermarkEraser1(
        is_watermark_predicate=_is_2514_watermark, watermark_orientations=(90,)
    ),
    "10.4028": WatermarkEraser4(doi4028_regexp, separator=" "),
    "10.4049": WatermarkEraser2(
        is_watermark_predicate=_is_downloaded_from_with_date,
        watermark_orientations=(90,),
        page_remover=ContentPageRemover(
            (0,), r"Related Content.*Downloaded from .* by guest on .*"
        ),
    ),
    "10.4103": WatermarkEraser4(precise_id_regexp, separator=" "),  # regex is correct
    "10.5325": BasePdfProcessor(
        page_remover=ContentPageRemover(
            (0,), r"For additional information about this article"
        )
    ),
    "10.7326": WatermarkEraser1(
        is_watermark_predicate=_is_7326_watermark, watermark_orientations=(0,)
    ),
    "10.7566": WatermarkEraser1(
        is_watermark_predicate=_is_7566_watermark, watermark_orientations=(0,)
    ),
    "10.14309": WatermarkEraser4(precise_id_regexp, separator=" "),  # regex is correct
    "10.17226": WatermarkEraser2(
        is_watermark_predicate=_is_17226_watermark,
        watermark_orientations=(0,),
        page_remover=ContentPageRemover(
            (0,),
            r"This PDF is protected by copyright and owned by the National Academy of Sciences",
        ),
    ),
    "10.23919": WatermarkEraser4(doi23919_regexp),
    "10.34067": WatermarkEraser4(precise_id_regexp, separator=" "),
    "10.35848": WatermarkEraser1(
        is_watermark_predicate=lambda text: False,
        page_remover=ContentPageRemover(
            (0,),
            r"To cite this article:.*This content was downloaded from IP address .* on .* at .*",
        ),
    ),
}

base_pdf_processor = BasePdfProcessor()
