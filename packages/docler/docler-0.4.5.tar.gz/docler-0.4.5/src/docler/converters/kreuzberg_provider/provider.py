"""Document converter using Kreuzberg's extraction."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import anyenv
import upath

from docler.common_types import TESSERACT_CODES
from docler.configs.converter_configs import KreuzbergConfig
from docler.converters.base import DocumentConverter
from docler.log import get_logger
from docler.mime_types import (
    HTML_MIME_TYPE,
    IMAGE_MIME_TYPES,
    PANDOC_SUPPORTED_MIME_TYPES,
    PDF_MIME_TYPE,
    PLAIN_TEXT_MIME_TYPES,
    POWER_POINT_MIME_TYPE,
    SPREADSHEET_MIME_TYPES,
)
from docler.models import Document


if TYPE_CHECKING:
    from datetime import datetime

    from docler.common_types import StrPath, SupportedLanguage


logger = get_logger(__name__)

# Kreuzberg metadata:

# class Metadata(TypedDict, total=False):
#     authors: NotRequired[list[str]]
#     categories: NotRequired[list[str]]
#     citations: NotRequired[list[str]]
#     comments: NotRequired[str]
#     copyright: NotRequired[str]
#     created_at: NotRequired[str]
#     created_by: NotRequired[str]
#     description: NotRequired[str]
#     fonts: NotRequired[list[str]]
#     height: NotRequired[int]
#     identifier: NotRequired[str]
#     keywords: NotRequired[list[str]]
#     languages: NotRequired[list[str]]
#     license: NotRequired[str]
#     modified_at: NotRequired[str]
#     modified_by: NotRequired[str]
#     organization: NotRequired[str | list[str]]
#     publisher: NotRequired[str]
#     references: NotRequired[list[str]]
#     status: NotRequired[str]
#     subject: NotRequired[str]
#     subtitle: NotRequired[str]
#     summary: NotRequired[str]
#     title: NotRequired[str]
#     version: NotRequired[str]
#     width: NotRequired[int]


class KreuzbergConverter(DocumentConverter[KreuzbergConfig]):
    """Document converter using Kreuzberg's extraction."""

    Config = KreuzbergConfig

    NAME = "kreuzberg"
    REQUIRED_PACKAGES: ClassVar = {"kreuzberg"}
    SUPPORTED_MIME_TYPES: ClassVar[set[str]] = (
        PLAIN_TEXT_MIME_TYPES
        | IMAGE_MIME_TYPES
        | PANDOC_SUPPORTED_MIME_TYPES
        | SPREADSHEET_MIME_TYPES
        | {PDF_MIME_TYPE, POWER_POINT_MIME_TYPE, HTML_MIME_TYPE}
    )

    def __init__(
        self,
        languages: list[SupportedLanguage] | None = None,
        *,
        force_ocr: bool = False,
    ):
        """Initialize the Kreuzberg converter.

        Args:
            languages: Language codes for OCR.
            force_ocr: Whether to force OCR even on digital documents.
        """
        super().__init__(languages=languages)
        self.force_ocr = force_ocr
        if languages:
            self.language = TESSERACT_CODES.get(languages[0])
        else:
            self.language = "eng"

    def _convert_path_sync(self, file_path: StrPath, mime_type: str) -> Document:
        """Convert a file using Kreuzberg.

        Args:
            file_path: Path to the file to process.
            mime_type: MIME type of the file.

        Returns:
            Converted document.
        """
        from kreuzberg import ExtractionConfig, extract_file

        local_file = upath.UPath(file_path)
        config = ExtractionConfig(force_ocr=self.force_ocr, extract_tables=True)
        result = anyenv.run_sync(extract_file(str(local_file), config=config))

        metadata = result.metadata
        created: datetime | None = None
        if date_str := metadata.pop("created_at", None):
            try:
                from dateutil import parser

                created = parser.parse(date_str)
            except Exception:  # noqa: BLE001
                pass
        authors = metadata.pop("authors", None)
        author = authors[0] if authors else None
        return Document(
            content=result.content,
            title=metadata.pop("title", None),
            author=metadata.pop("created_by", None) or author,
            created=created,
            source_path=str(local_file),
            mime_type=result.mime_type or mime_type,
            metadata=metadata,  # pyright: ignore
        )


if __name__ == "__main__":
    pdf_path = "src/docler/resources/pdf_sample.pdf"
    converter = KreuzbergConverter(force_ocr=True)
    result = anyenv.run_sync(converter.convert_file(pdf_path))
    print(result)
