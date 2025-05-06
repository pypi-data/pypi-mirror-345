from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.schemas.token import BaseTokenSchemas
from maleo_foundation.models.transfers.general.token import BaseTokenGeneralTransfers

class BaseTokenParametersTransfers:
    class Encode(
        BaseTokenSchemas.Password,
        BaseTokenSchemas.Key
    ):
        payload:BaseTokenGeneralTransfers.BaseEncodePayload = Field(..., description="Encode payload")

    class Decode(
        BaseTokenSchemas.Token,
        BaseTokenSchemas.Key
    ): pass