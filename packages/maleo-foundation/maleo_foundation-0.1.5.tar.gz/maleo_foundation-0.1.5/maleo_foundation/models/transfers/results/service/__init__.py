from __future__ import annotations
from .general import BaseServiceGeneralResultsTransfers
from .query import BaseServiceQueryResultsTransfers
from .controllers import BaseServiceControllerResultsTransfers

class BaseServiceResultsTransfers:
    General = BaseServiceGeneralResultsTransfers
    Query = BaseServiceQueryResultsTransfers
    Controller = BaseServiceControllerResultsTransfers