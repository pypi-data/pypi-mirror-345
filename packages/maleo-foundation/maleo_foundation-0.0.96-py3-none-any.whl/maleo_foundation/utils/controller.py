from fastapi import status
from functools import wraps
from typing import Awaitable, Callable, Dict, List, Type, Any
from maleo_foundation.types import BaseTypes
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.responses import BaseResponses
from maleo_foundation.models.transfers.parameters.general import BaseGeneralParametersTransfers
from maleo_foundation.models.transfers.parameters.service import BaseServiceParametersTransfers
from maleo_foundation.models.transfers.results.service.controllers.rest import BaseServiceRESTControllerResults
from maleo_foundation.expanded_types.general import BaseGeneralExpandedTypes
from maleo_foundation.expanded_types.service import ExpandedServiceTypes

class BaseControllerUtils:
    @staticmethod
    def check_unique_existence(
        check:BaseServiceParametersTransfers.UniqueFieldCheck,
        get_single_parameters_class:Type[ExpandedServiceTypes.GetSingleParameter],
        get_single_service_function:ExpandedServiceTypes.SyncGetSingleFunction,
        create_failed_response_class:Type[BaseResponses.Fail],
        update_failed_response_class:Type[BaseResponses.Fail],
        **additional_get_parameters:Any
    ) -> BaseServiceRESTControllerResults:
        """Generic helper function to check if a unique value exists in the database."""

        #* Return early if nullable and no new value
        if check.nullable and check.new_value is None:
            return BaseServiceRESTControllerResults(success=True, content=None)

        #* Return early if values are unchanged on update
        if check.operation == BaseEnums.OperationType.UPDATE and check.old_value == check.new_value:
            return BaseServiceRESTControllerResults(success=True, content=None)

        #* Prepare parameters to query for existing data
        get_single_parameters = get_single_parameters_class(identifier=check.field, value=check.new_value)

        #* Query the existing data using provided function
        service_result:ExpandedServiceTypes.GetSingleResult = get_single_service_function(parameters=get_single_parameters, **additional_get_parameters)
        if not service_result.success:
            content = BaseResponses.ServerError.model_validate(service_result.model_dump(exclude_unset=True)).model_dump()
            return BaseServiceRESTControllerResults(success=False, content=content, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #* Handle case if duplicate is found
        if service_result.data:
            description = f"External error: {check.field} of '{check.new_value}' already exists in the database"
            other = check.suggestion or f"Select another {check.field} value"
            if check.operation == BaseEnums.OperationType.CREATE:
                content = create_failed_response_class(description=description, other=other).model_dump()
            elif check.operation == BaseEnums.OperationType.UPDATE:
                content = update_failed_response_class(description=description, other=other).model_dump()

            return BaseServiceRESTControllerResults(success=False, content=content, status_code=status.HTTP_400_BAD_REQUEST)

        #* No duplicates found
        return BaseServiceRESTControllerResults(success=True, content=None)

    @staticmethod
    def field_expansion_handler(
        expandable_fields_dependencies_map:BaseTypes.OptionalStringToListOfStringDict = None,
        field_expansion_processors:BaseGeneralExpandedTypes.OptionalListOfFieldExpansionProcessor = None
    ):
        """
        Decorator to handle expandable fields validation and processing.
        
        Args:
            expandable_fields_dependencies_map: Dictionary where keys are dependency fields and values are lists of dependent fields
            field_expansion_processors: List of processor functions that handle that field's data
        """
        def decorator(func:Callable[..., Awaitable[BaseServiceRESTControllerResults]]):
            @wraps(func)
            async def wrapper(parameters, *args, **kwargs):
                expand:BaseTypes.OptionalListOfStrings = getattr(parameters, 'expand', None)

                #* Validate expandable fields dependencies
                if expand is not None and expandable_fields_dependencies_map is not None:
                    for dependency, dependents in expandable_fields_dependencies_map.items():
                        if dependency not in expand:
                            for dependent in dependents:
                                if dependent in expand:
                                    other = f"'{dependency}' must also be expanded if '{dependent}' is expanded"
                                    content = BaseResponses.InvalidExpand(other=other).model_dump()
                                    return BaseServiceRESTControllerResults(success=False, content=content, status_code=status.HTTP_400_BAD_REQUEST)

                #* Call the original function
                result = await func(parameters, *args, **kwargs)

                if not isinstance(result.content, Dict):
                    return result

                #* Process the fields if needed
                if result.success and result.content.get("data", None) is not None and field_expansion_processors is not None:
                    data = result.content["data"]
                    if isinstance(data, List):
                        for idx, dt in enumerate(data):
                            for processor in field_expansion_processors:
                                raw_parameters = {"data": dt, "expand": expand}
                                parameters = BaseGeneralParametersTransfers.FieldExpansionProcessor.model_validate(raw_parameters)
                                dt = processor(parameters)
                                data[idx] = dt
                    elif isinstance(data, Dict):
                        raw_parameters = {"data": data, "expand": expand}
                        parameters = BaseGeneralParametersTransfers.FieldExpansionProcessor.model_validate(raw_parameters)
                        for processor in field_expansion_processors:
                            data = processor(parameters)
                    result.content["data"] = data
                    result.process_response()

                return result
            return wrapper
        return decorator