from typing import Awaitable, Callable, Union
from maleo_foundation.models.transfers.parameters.general import BaseGeneralParametersTransfers
from maleo_foundation.models.transfers.parameters.service import BaseServiceParametersTransfers
from maleo_foundation.models.transfers.results.service.query import BaseServiceQueryResultsTransfers

class ExpandedQueryTypes:
    #* Unpaginated multiple data
    GetUnpaginatedMultipleParameter = BaseServiceParametersTransfers.GetUnpaginatedMultiple
    GetUnpaginatedMultipleResult = Union[
        BaseServiceQueryResultsTransfers.Fail,
        BaseServiceQueryResultsTransfers.NoData,
        BaseServiceQueryResultsTransfers.UnpaginatedMultipleData
    ]
    SyncGetUnpaginatedMultipleFunction = Callable[
        [GetUnpaginatedMultipleParameter],
        GetUnpaginatedMultipleResult
    ]
    AsyncGetUnpaginatedMultipleFunction = Callable[
        [GetUnpaginatedMultipleParameter],
        Awaitable[GetUnpaginatedMultipleResult]
    ]

    #* Paginated multiple data
    GetPaginatedMultipleParameter = BaseServiceParametersTransfers.GetPaginatedMultiple
    GetPaginatedMultipleResult = Union[
        BaseServiceQueryResultsTransfers.Fail,
        BaseServiceQueryResultsTransfers.NoData,
        BaseServiceQueryResultsTransfers.PaginatedMultipleData
    ]
    SyncGetPaginatedMultipleFunction = Callable[
        [GetPaginatedMultipleParameter],
        GetPaginatedMultipleResult
    ]
    AsyncGetPaginatedMultipleFunction = Callable[
        [GetPaginatedMultipleParameter],
        Awaitable[GetPaginatedMultipleResult]
    ]

    #* Single data
    GetSingleParameter = BaseGeneralParametersTransfers.GetSingle
    GetSingleResult = Union[
        BaseServiceQueryResultsTransfers.Fail,
        BaseServiceQueryResultsTransfers.NoData,
        BaseServiceQueryResultsTransfers.SingleData
    ]
    SyncGetSingleFunction = Callable[
        [GetSingleParameter],
        GetSingleResult
    ]
    AsyncGetSingleFunction = Callable[
        [GetSingleParameter],
        Awaitable[GetSingleResult]
    ]

    #* Create or Update
    CreateOrUpdateResult = Union[
        BaseServiceQueryResultsTransfers.Fail,
        BaseServiceQueryResultsTransfers.SingleData
    ]

    #* Status update
    StatusUpdateResult = Union[
        BaseServiceQueryResultsTransfers.Fail,
        BaseServiceQueryResultsTransfers.SingleData
    ]