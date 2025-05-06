from __future__ import annotations
from .formatter import BaseFormatter
from .logger import BaseLogger
from .exceptions import BaseExceptions
from .controller import BaseControllerUtils
from .query import BaseQueryUtils

class BaseUtils:
    Formatter = BaseFormatter
    Logger = BaseLogger
    Exceptions = BaseExceptions
    Controller = BaseControllerUtils
    Query = BaseQueryUtils