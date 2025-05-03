from maleo_foundation.models.transfers.results.service.general import BaseServiceGeneralResultsTransfers
from maleo_foundation.models.schemas.token import BaseTokenSchemas
from maleo_foundation.models.transfers.general.token import BaseTokenGeneralTransfers

class BaseTokenResultsTransfers:
    class Fail(BaseServiceGeneralResultsTransfers.Fail): pass

    class Encode(BaseServiceGeneralResultsTransfers.SingleData):
        data:BaseTokenSchemas.Token

    class Decode(BaseServiceGeneralResultsTransfers.SingleData):
        data:BaseTokenGeneralTransfers.DecodePayload