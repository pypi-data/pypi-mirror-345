from . import schemathesis
from ._version import VERSION
from .http import HttpInteraction, HttpRequest, HttpResponse  # noqa: F401

__version__ = VERSION

try:
    # Try professional first, fall back to community
    try:
        from tracecov_professional import CoverageMap  # noqa: F401

        __edition__ = "professional"
    except ImportError:
        from tracecov_community import CoverageMap  # noqa: F401

        __edition__ = "community"
except ImportError as exc:
    raise ImportError(
        "No TraceCov implementation found. Please install either 'tracecov[community]' or 'tracecov-professional'."
    ) from exc


__all__ = [
    "__version__",
    "__edition__",
    "HttpInteraction",
    "HttpRequest",
    "HttpResponse",
    "CoverageMap",
    "schemathesis",
]
