from typing import Union
from maleo_foundation.models.transfers.results.token import BaseTokenResultsTransfers

class BaseTokenResultsTypes:
    Encode = Union[
        BaseTokenResultsTransfers.Fail,
        BaseTokenResultsTransfers.Encode
    ]

    Decode = Union[
        BaseTokenResultsTransfers.Fail,
        BaseTokenResultsTransfers.Decode
    ]