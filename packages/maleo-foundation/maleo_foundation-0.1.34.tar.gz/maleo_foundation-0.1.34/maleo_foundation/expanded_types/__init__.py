from __future__ import annotations
from .general import BaseGeneralExpandedTypes
from .query import ExpandedQueryTypes
from .service import ExpandedServiceTypes
from .client import ExpandedClientTypes

class BaseExpandedTypes:
    General = BaseGeneralExpandedTypes
    Query = ExpandedQueryTypes
    Service = ExpandedServiceTypes
    Client = ExpandedClientTypes