from __future__ import annotations

import importlib.metadata

# Distribution name, not __name__: this module is ocrmypdf_rapidocr.version.
_DISTRIBUTION = "ocrmypdf-rapidocr"

try:
    __version__ = importlib.metadata.version(_DISTRIBUTION)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
