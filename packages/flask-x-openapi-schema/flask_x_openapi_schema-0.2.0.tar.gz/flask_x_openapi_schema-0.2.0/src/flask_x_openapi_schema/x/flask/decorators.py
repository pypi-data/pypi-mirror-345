"""Decorators for adding OpenAPI metadata to Flask MethodView endpoints.

This module provides decorators that can be used to add OpenAPI metadata to Flask MethodView
endpoints. The decorators handle parameter binding for request data, including request body,
query parameters, path parameters, and file uploads.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from flask import request
from pydantic import BaseModel

from flask_x_openapi_schema import get_logger
from flask_x_openapi_schema.core.config import ConventionalPrefixConfig
from flask_x_openapi_schema.core.decorator_base import DecoratorBase, OpenAPIDecoratorBase
from flask_x_openapi_schema.i18n.i18n_string import I18nStr
from flask_x_openapi_schema.models.content_types import RequestContentTypes, ResponseContentTypes
from flask_x_openapi_schema.models.responses import OpenAPIMetaResponse


class FlaskOpenAPIDecorator(DecoratorBase):
    """OpenAPI metadata decorator for Flask MethodView.

    This class implements a decorator that adds OpenAPI metadata to Flask MethodView
    endpoints and handles parameter binding for request data.
    """

    def __init__(
        self,
        summary: str | I18nStr | None = None,
        description: str | I18nStr | None = None,
        tags: list[str] | None = None,
        operation_id: str | None = None,
        responses: OpenAPIMetaResponse | None = None,
        deprecated: bool = False,
        security: list[dict[str, list[str]]] | None = None,
        external_docs: dict[str, str] | None = None,
        language: str | None = None,
        prefix_config: ConventionalPrefixConfig | None = None,
        content_type: str | None = None,
        request_content_types: RequestContentTypes | None = None,
        response_content_types: ResponseContentTypes | None = None,
        content_type_resolver: Callable[[Any], str] | None = None,
    ) -> None:
        """Initialize the decorator with OpenAPI metadata parameters.

        Args:
            summary: A short summary of what the operation does
            description: A verbose explanation of the operation behavior
            tags: A list of tags for API documentation control
            operation_id: Unique string used to identify the operation
            responses: The responses the API can return
            deprecated: Declares this operation to be deprecated
            security: A declaration of which security mechanisms can be used for this operation
            external_docs: Additional external documentation
            language: Language code to use for I18nString values
            prefix_config: Configuration object for parameter prefixes
            content_type: Custom content type for request body. If None, will be auto-detected.
            request_content_types: Multiple content types for request body.
            response_content_types: Multiple content types for response body.
            content_type_resolver: Function to determine content type based on request.

        """
        super().__init__(
            summary=summary,
            description=description,
            tags=tags,
            operation_id=operation_id,
            responses=responses,
            deprecated=deprecated,
            security=security,
            external_docs=external_docs,
            language=language,
            prefix_config=prefix_config,
            content_type=content_type,
            request_content_types=request_content_types,
            response_content_types=response_content_types,
            content_type_resolver=content_type_resolver,
        )
        self.framework = "flask"
        self.base_decorator = None

    def __call__(self, func: Callable) -> Callable:
        """Apply the decorator to the function.

        Args:
            func: The function to decorate

        Returns:
            The decorated function

        """
        if self.base_decorator is None:
            self.base_decorator = OpenAPIDecoratorBase(
                summary=self.summary,
                description=self.description,
                tags=self.tags,
                operation_id=self.operation_id,
                responses=self.responses,
                deprecated=self.deprecated,
                security=self.security,
                external_docs=self.external_docs,
                language=self.language,
                prefix_config=self.prefix_config,
                framework=self.framework,
                content_type=self.content_type,
                request_content_types=self.request_content_types,
                response_content_types=self.response_content_types,
                content_type_resolver=self.content_type_resolver,
            )
        return self.base_decorator(func)

    def extract_parameters_from_models(
        self,
        query_model: type[BaseModel] | None,
        path_params: list[str] | None,
    ) -> list[dict[str, Any]]:
        """Extract OpenAPI parameters from models.

        Args:
            query_model: The query parameter model
            path_params: List of path parameter names

        Returns:
            List of OpenAPI parameter objects

        """
        parameters = [
            {
                "name": param,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
            }
            for param in path_params
        ]

        if query_model:
            schema = query_model.model_json_schema()
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            for field_name, field_schema in properties.items():
                param = {
                    "name": field_name,
                    "in": "query",
                    "required": field_name in required,
                    "schema": field_schema,
                }

                if "description" in field_schema:
                    param["description"] = field_schema["description"]

                parameters.append(param)

        return parameters

    def process_request_body(self, param_name: str, model: type[BaseModel], kwargs: dict[str, Any]) -> dict[str, Any]:
        """Process request body parameters for Flask.

        Args:
            param_name: The parameter name to bind the model instance to
            model: The Pydantic model class to use for validation
            kwargs: The keyword arguments to update

        Returns:
            Updated kwargs dictionary with the model instance

        """
        from flask import request

        from flask_x_openapi_schema.models.file_models import FileField

        if hasattr(model, "model_fields") and hasattr(request, "files") and request.files:
            has_file_fields = False
            for field_info in model.model_fields.values():
                field_type = field_info.annotation

                if isinstance(field_type, type) and issubclass(field_type, FileField):
                    has_file_fields = True
                    break

                origin = getattr(field_type, "__origin__", None)
                if origin is list or origin is list:
                    args = getattr(field_type, "__args__", [])
                    if args and isinstance(args[0], type) and issubclass(args[0], FileField):
                        has_file_fields = True
                        break

            if has_file_fields:
                model_data = dict(request.form.items())
                for field_name in model.model_fields:
                    if field_name in request.files:
                        model_data[field_name] = request.files[field_name]

                if model_data:
                    try:
                        model_instance = model(**model_data)
                        kwargs[param_name] = model_instance
                    except Exception as e:
                        logger = get_logger(__name__)
                        logger.exception(
                            f"Failed to create model instance with mock files for {model.__name__}", exc_info=e
                        )
                    else:
                        return kwargs

        return super().process_request_body(param_name, model, kwargs)

    def process_query_params(self, param_name: str, model: type[BaseModel], kwargs: dict[str, Any]) -> dict[str, Any]:
        """Process query parameters for Flask.

        Args:
            param_name: The parameter name to bind the model instance to
            model: The Pydantic model class to use for validation
            kwargs: The keyword arguments to update

        Returns:
            Updated kwargs dictionary with the model instance

        """
        query_data = {}
        model_fields = model.model_fields

        for field_name in model_fields:
            if field_name in request.args:
                query_data[field_name] = request.args.get(field_name)

        model_instance = model(**query_data)

        kwargs[param_name] = model_instance

        return kwargs

    def process_additional_params(self, kwargs: dict[str, Any], param_names: list[str]) -> dict[str, Any]:
        """Process additional framework-specific parameters.

        Args:
            kwargs: The keyword arguments to update
            param_names: List of parameter names that have been processed

        Returns:
            Updated kwargs dictionary

        """
        logger = get_logger(__name__)
        logger.debug(f"Processing additional parameters with kwargs keys: {list(kwargs.keys())}")
        logger.debug(f"Processed parameter names: {param_names}")
        return kwargs


F = TypeVar("F", bound=Callable[..., Any])


def openapi_metadata(
    *,
    summary: str | I18nStr | None = None,
    description: str | I18nStr | None = None,
    tags: list[str] | None = None,
    operation_id: str | None = None,
    responses: OpenAPIMetaResponse | None = None,
    deprecated: bool = False,
    security: list[dict[str, list[str]]] | None = None,
    external_docs: dict[str, str] | None = None,
    language: str | None = None,
    prefix_config: ConventionalPrefixConfig | None = None,
    content_type: str | None = None,
    request_content_types: RequestContentTypes | None = None,
    response_content_types: ResponseContentTypes | None = None,
    content_type_resolver: Callable[[Any], str] | None = None,
) -> Callable[[F], F]:
    """Decorator to add OpenAPI metadata to a Flask MethodView endpoint.

    This decorator adds OpenAPI metadata to a Flask MethodView endpoint and handles
    parameter binding for request data. It automatically binds request body, query parameters,
    path parameters, and file uploads to function parameters based on their type annotations
    and parameter name prefixes.

    Args:
        summary: A short summary of what the operation does
        description: A verbose explanation of the operation behavior
        tags: A list of tags for API documentation control
        operation_id: Unique string used to identify the operation
        responses: The responses the API can return
        deprecated: Declares this operation to be deprecated
        security: A declaration of which security mechanisms can be used for this operation
        external_docs: Additional external documentation
        language: Language code to use for I18nString values (default: current language)
        prefix_config: Configuration object for parameter prefixes
        content_type: Custom content type for request body. If None, will be auto-detected.
        request_content_types: Multiple content types for request body.
        response_content_types: Multiple content types for response body.
        content_type_resolver: Function to determine content type based on request.


    Returns:
        The decorated function with OpenAPI metadata attached

    Examples:
        >>> from flask.views import MethodView
        >>> from flask_x_openapi_schema.x.flask import openapi_metadata
        >>> from flask_x_openapi_schema import OpenAPIMetaResponse, OpenAPIMetaResponseItem
        >>> from pydantic import BaseModel, Field
        >>>
        >>> class ItemRequest(BaseModel):
        ...     name: str = Field(..., description="Item name")
        ...     price: float = Field(..., description="Item price")
        >>>
        >>> class ItemResponse(BaseModel):
        ...     id: str = Field(..., description="Item ID")
        ...     name: str = Field(..., description="Item name")
        ...     price: float = Field(..., description="Item price")
        >>>
        >>> class ItemView(MethodView):
        ...     @openapi_metadata(
        ...         summary="Create a new item",
        ...         description="Create a new item with the provided information",
        ...         tags=["items"],
        ...         operation_id="createItem",
        ...         responses=OpenAPIMetaResponse(
        ...             responses={
        ...                 "201": OpenAPIMetaResponseItem(model=ItemResponse, description="Item created successfully"),
        ...                 "400": OpenAPIMetaResponseItem(description="Invalid request data"),
        ...             }
        ...         ),
        ...     )
        ...     def post(self, _x_body: ItemRequest):
        ...         item = {"id": "123", "name": _x_body.name, "price": _x_body.price}
        ...         return item, 201

    """
    return FlaskOpenAPIDecorator(
        summary=summary,
        description=description,
        tags=tags,
        operation_id=operation_id,
        responses=responses,
        deprecated=deprecated,
        security=security,
        external_docs=external_docs,
        language=language,
        prefix_config=prefix_config,
        content_type=content_type,
        request_content_types=request_content_types,
        response_content_types=response_content_types,
        content_type_resolver=content_type_resolver,
    )
