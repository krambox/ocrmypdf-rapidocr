import importlib.metadata

from ocrmypdf_rapidocr import __version__


def test_version_matches_distribution() -> None:
    assert __version__ == importlib.metadata.version("ocrmypdf-rapidocr")
    assert __version__ != "0.0.0"
