from __future__ import annotations
from .formatter import BaseFormatter
from .exceptions import BaseExceptions
from .extractor import BaseExtractors
from .keyloader import BaseKeyLoaders
from .controller import BaseControllerUtils
from .query import BaseQueryUtils

class BaseUtils:
    Formatter = BaseFormatter
    Exceptions = BaseExceptions
    Extractors = BaseExtractors
    KeyLoader = BaseKeyLoaders
    Controller = BaseControllerUtils
    Query = BaseQueryUtils