from types import SimpleNamespace

import pytest
from ocrmypdf.exceptions import BadArgsError

from ocrmypdf_rapidocr.hocr import build_hocr_document
from ocrmypdf_rapidocr.languages import select_single_language


def test_deu_plus_eng_selects_german() -> None:
    options = SimpleNamespace(languages=["deu", "eng"])
    assert select_single_language(options) == "deu"


def test_deu_eng_combination_string_selects_german() -> None:
    options = SimpleNamespace(languages=["deu+eng"])
    assert select_single_language(options) == "deu"


def test_other_combination_is_rejected() -> None:
    options = SimpleNamespace(languages=["eng", "fra"])
    with pytest.raises(BadArgsError):
        select_single_language(options)


def test_hocr_page_carries_scan_res() -> None:
    hocr = build_hocr_document(
        page_width=100,
        page_height=200,
        language="deu",
        lines=[],
        dpi_x=400,
        dpi_y=400,
    )
    assert 'title="bbox 0 0 100 200; scan_res 400 400"' in hocr
