from __future__ import annotations

import importlib.metadata
from functools import lru_cache
from pathlib import Path

from ocrmypdf.pluginspec import OcrEngine, OrientationConfidence
from PIL import Image

from ocrmypdf_rapidocr.hocr import build_hocr_document, extract_hocr_lines
from ocrmypdf_rapidocr.languages import (
    SUPPORTED_LANGUAGE_CODES,
    map_language_to_langrec_name,
    select_single_language,
)
from ocrmypdf_rapidocr.options import get_option_config_path
from ocrmypdf_rapidocr.version import __version__


def _import_rapidocr_symbols():
    from rapidocr import EngineType, LangRec, ModelType, OCRVersion, RapidOCR

    return RapidOCR, LangRec, EngineType, ModelType, OCRVersion


def _image_dpi(image: Image.Image) -> tuple[int, int]:
    raw = image.info.get("dpi")
    if isinstance(raw, tuple) and len(raw) >= 2:
        dpi_x = int(round(float(raw[0])))
        dpi_y = int(round(float(raw[1])))
        if dpi_x > 0 and dpi_y > 0:
            return dpi_x, dpi_y
    # OCRmyPDF rasterizes below-threshold scans at about 400 DPI.
    return 400, 400


def _german_params() -> dict[str, object]:
    """Same checkpoints Docling uses for PP-OCRv6 small on ONNX Runtime."""
    _, _, EngineType, ModelType, OCRVersion = _import_rapidocr_symbols()
    return {
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Cls.engine_type": EngineType.ONNXRUNTIME,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Det.ocr_version": OCRVersion.PPOCRV6,
        "Det.lang_type": "ch",
        "Det.model_type": ModelType.SMALL,
        "Cls.ocr_version": OCRVersion.PPOCRV4,
        "Cls.lang_type": "ch",
        "Cls.model_type": ModelType.MOBILE,
        "Rec.ocr_version": OCRVersion.PPOCRV6,
        "Rec.lang_type": "de",
        "Rec.model_type": ModelType.SMALL,
    }


@lru_cache(maxsize=16)
def get_rapidocr_engine(language: str, config_path: str | None):
    RapidOCR, LangRec, EngineType, _, _ = _import_rapidocr_symbols()

    if language == "deu":
        params = _german_params()
    else:
        langrec_name = map_language_to_langrec_name(language)
        langrec_value = getattr(LangRec, langrec_name)
        params = {
            "Det.engine_type": EngineType.ONNXRUNTIME,
            "Cls.engine_type": EngineType.ONNXRUNTIME,
            "Rec.engine_type": EngineType.ONNXRUNTIME,
            "Rec.lang_type": langrec_value,
        }
    return RapidOCR(config_path=config_path, params=params)


class RapidOCREngine(OcrEngine):
    @staticmethod
    def version() -> str:
        try:
            return importlib.metadata.version("rapidocr")
        except importlib.metadata.PackageNotFoundError:
            return "unknown"

    @staticmethod
    def creator_tag(options) -> str:
        return (
            f"RapidOCR {RapidOCREngine.version()} via ocrmypdf-rapidocr {__version__}"
        )

    def __str__(self) -> str:
        return f"RapidOCR {RapidOCREngine.version()}"

    @staticmethod
    def languages(options) -> set[str]:
        return set(SUPPORTED_LANGUAGE_CODES)

    @staticmethod
    def get_orientation(input_file, options) -> OrientationConfidence:
        return OrientationConfidence(angle=0, confidence=0.0)

    @staticmethod
    def get_deskew(input_file, options) -> float:
        return 0.0

    @staticmethod
    def generate_hocr(input_file, output_hocr, output_text, options) -> None:
        language = select_single_language(options)
        config_path = get_option_config_path(options)
        rapidocr_engine = get_rapidocr_engine(
            language,
            config_path,
        )

        with Image.open(input_file) as image:
            page_width, page_height = image.size
            dpi_x, dpi_y = _image_dpi(image)

        result = rapidocr_engine(str(input_file))
        lines = extract_hocr_lines(
            result, page_width=page_width, page_height=page_height
        )
        hocr = build_hocr_document(
            page_width=page_width,
            page_height=page_height,
            language=language,
            lines=lines,
            dpi_x=dpi_x,
            dpi_y=dpi_y,
        )
        plain_text = "\n".join(text for text, _bbox, _confidence in lines)

        Path(output_hocr).write_text(hocr, encoding="utf-8")
        Path(output_text).write_text(plain_text, encoding="utf-8")

    @staticmethod
    def generate_pdf(input_file, output_pdf, output_text, options) -> None:
        raise NotImplementedError(
            "ocrmypdf-rapidocr does not support sandwich renderer. "
            "Use --pdf-renderer auto or --pdf-renderer fpdf2."
        )
