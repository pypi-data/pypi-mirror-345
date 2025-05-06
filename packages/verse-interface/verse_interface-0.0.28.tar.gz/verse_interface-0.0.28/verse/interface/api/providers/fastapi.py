from __future__ import annotations

__all__ = ["FastAPI"]

import asyncio
import inspect
from typing import Any, Callable

import uvicorn
from fastapi import APIRouter, Depends
from fastapi import FastAPI as BaseFastAPI
from fastapi import HTTPException, Request, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBearer,
    SecurityScopes,
)
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from starlette.middleware.cors import CORSMiddleware

from verse.core import (
    Context,
    DataAccessor,
    DataModel,
    Operation,
    OperationParser,
    Provider,
    Response,
    TypeConverter,
)
from verse.core.exceptions import BaseError
from verse.core.spec import ComponentSpec, SpecBuilder

from .._helper import get_operations, get_return_type
from .._models import (
    APIAuth,
    APIAuthType,
    APIInfo,
    ArgSourceType,
    ComponentMapping,
    OperationMapping,
)
from .._operation import APIOperation

app = None


class FastAPI(Provider):
    host: str | None
    port: int | None
    reload: bool
    workers: int
    root_path: str | None
    openapi_url: str | None
    cors_origins: str | list[str] | None
    cors_methods: str | list[str] | None
    cors_headers: str | list[str] | None
    cors_credentials: bool | None
    nparams: dict[str, Any]

    _app: BaseFastAPI

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        reload: bool = False,
        workers: int = 1,
        root_path: str | None = None,
        openapi_url: str | None = "/openapi.json",
        cors_origins: str | list[str] | None = None,
        cors_methods: str | list[str] | None = "*",
        cors_headers: str | list[str] | None = "*",
        cors_credentials: bool | None = True,
        nparams: dict[str, Any] = dict(),
        **kwargs,
    ):
        """Initialize.

        Args:
            host:
                Host IP address.
            port:
                HTTP port.
            reload:
                A value indicating whether the app should be reloaded
                when any files are modified.
            workers:
                Number of uvicorn worker processes.
            root_path:
                Root path for the app.
            openapi_url:
                OpenAPI URL for the app.
            cors_origins:
                Allowed origins for CORS.
                If None, CORS middleware is not enabled.
            cors_methods:
                Allowed methods for CORS.
                Defaults to *.
            cors_headers:
                Allowed headers for CORS.
                Defaults to *.
            cors_credentials:
                A value indicating whether credentials
                are allowed for CORS. Defaults to true.
            nparams:
                Native parameters to FastAPI and uvicorn client.
        """
        self.host = host
        self.port = port
        self.reload = reload
        self.workers = workers
        self.root_path = root_path
        self.openapi_url = openapi_url
        self.cors_origins = cors_origins
        self.cors_methods = cors_methods
        self.cors_headers = cors_headers
        self.cors_credentials = cors_credentials
        self.nparams = nparams
        self._app = BaseFastAPI(
            root_path=self.root_path or "",
            openapi_url=self.openapi_url,
            **self.nparams,
        )

    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        result = None
        op_parser = OperationParser(operation)
        if op_parser.op_equals(APIOperation.GET_INFO):
            result = self._get_info()
            return Response(result=result)
        else:
            component_mappings = self._get_component_mappings()
            for component_mapping in component_mappings:
                api = GenericAPI(component_mapping, self.get_component().auth)
                self._app.include_router(
                    api.router,
                    prefix=component_mapping.prefix,
                )
            server = self._get_server()
            try:
                asyncio.run(server.serve())
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                pass
        return Response(result=result)

    async def __arun__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        result = None
        op_parser = OperationParser(operation)
        if op_parser.op_equals(APIOperation.GET_INFO):
            result = self._get_info()
        else:
            component_mappings = self._get_component_mappings()
            for component_mapping in component_mappings:
                api = GenericAsyncAPI(
                    component_mapping, self.get_component().auth
                )
                self._app.include_router(
                    api.router,
                    prefix=component_mapping.prefix,
                )
            server = self._get_server()
            try:
                await server.serve()
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                pass
        return Response(result=result)

    def _get_component_mappings(self) -> list[ComponentMapping]:
        if self.get_component().component:
            return [ComponentMapping(component=self.get_component().component)]
        return self.get_component().components

    def _get_server(self) -> uvicorn.Server:
        if self.cors_origins:
            allow_origins = (
                [self.cors_origins]
                if isinstance(self.cors_origins, str)
                else self.cors_origins
            )
            allow_methods = (
                [self.cors_methods]
                if isinstance(self.cors_methods, str)
                else self.cors_methods
            )
            allow_headers = (
                [self.cors_headers]
                if isinstance(self.cors_headers, str)
                else self.cors_headers
            )
            allow_credentials = self.cors_credentials
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=allow_origins,
                allow_credentials=allow_credentials,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
            )
        if self.reload is False and self.workers == 1:
            config = uvicorn.Config(
                self._app,
                host=self.host or self.get_component().host,
                port=self.port or self.get_component().port,
                reload=self.reload,
                workers=self.workers,
            )
            server = uvicorn.Server(config)
            return server
        else:
            global app
            app = self._app
            config = uvicorn.Config(
                self._get_app_string(),
                host=self.host or self.get_component().host,
                port=self.port or self.get_component().port,
                reload=self.reload,
                workers=self.workers,
            )
            server = uvicorn.Server(config)
            return server

    def _get_app_string(self) -> str:
        module = inspect.getmodule(self)
        if module is not None:
            return f"{module.__name__}:app"
        raise ModuleNotFoundError("Module not found")

    def _get_info(self) -> APIInfo:
        return APIInfo(
            host=self.host or self.get_component().host,
            port=self.port or self.get_component().port,
        )


class RunRequest(DataModel):
    operation: Operation | None = None
    context: Context | None = None


class BaseAPI:
    component_mapping: ComponentMapping
    router: APIRouter
    auth: APIAuth | None

    def __init__(
        self,
        component_mapping: ComponentMapping,
        auth: APIAuth | None = None,
    ):
        self.component_mapping = component_mapping
        self.auth = auth
        self.router = APIRouter()
        self.init_routes()

    def get_path(self, operation_name: str) -> str:
        for operation in self.component_mapping.operations:
            if operation.name == operation_name:
                return operation.path or f"/{operation_name}"
        return f"/{operation_name}"

    def get_http_method(self, operation_name: str) -> str:
        for operation in self.component_mapping.operations:
            if operation.name == operation_name:
                return operation.method.upper()
        return "POST"

    def init_routes(self) -> None:
        operations = get_operations(self.component_mapping.component)
        for operation_name, operation_method in operations.items():
            http_method = "POST"
            path = f"/{operation_name}"
            status_code = None
            auth = self.component_mapping.auth or self.auth
            operation_mapping = self._get_operation_mapping(operation_name)
            if operation_mapping:
                http_method = operation_mapping.method.upper()
                path = operation_mapping.path or f"/{operation_name}"
                status_code = operation_mapping.status_code
                auth = auth or operation_mapping.auth
            if auth and auth.type == APIAuthType.API_KEY:
                if auth.config and auth.config.header:
                    security_scheme: Any = APIKeyHeader(
                        name=auth.config.header, auto_error=True
                    )
                elif auth.config and auth.config.query:
                    security_scheme = APIKeyQuery(
                        name=auth.config.query, auto_error=True
                    )
                else:
                    security_scheme = APIKeyHeader(
                        name="Authorization", auto_error=True
                    )
            elif auth and auth.type == APIAuthType.BEARER_TOKEN:
                security_scheme = HTTPBearer(auto_error=True)
            elif auth and auth.type == APIAuthType.BASIC:
                security_scheme = HTTPBasic(auto_error=True)
            else:
                security_scheme = None

            def create_auth_validate_method(auth, security_scheme) -> Callable:
                def auth_validate(credentials=Security(security_scheme)):
                    if security_scheme is None:
                        return dict()

                    from verse.identity.authentication import Authentication

                    if isinstance(auth.component, Authentication):
                        if isinstance(security_scheme, APIKeyHeader):
                            if security_scheme.model.name == "Authorization":
                                start = len("Bearer ")
                                return auth.component.validate(
                                    credentials.credentials[start:]
                                )
                            return auth.component.validate(credentials)
                        elif isinstance(security_scheme, APIKeyQuery):
                            return auth.component.validate(credentials)
                        elif isinstance(security_scheme, HTTPBearer):
                            return auth.component.validate(
                                credentials.credentials
                            )
                        elif isinstance(security_scheme, HTTPBasic):
                            return auth.component.validate(
                                credentials.username, credentials.password
                            )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=(
                                "Auth component is not an instance of "
                                "Authentication"
                            ),
                        )

                return auth_validate

            def create_wrapped_operation_method(
                method: Callable,
                operation_mapping: OperationMapping | None,
                auth_validate: Callable,
            ) -> Callable:
                sig = inspect.signature(method)
                params = list(sig.parameters.values())

                auth_param = inspect.Parameter(
                    "__auth__",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(auth_validate),
                )

                request_param = inspect.Parameter(
                    "__request__",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=None,
                    annotation=Request,
                )

                for i, p in enumerate(params):
                    if p.kind == inspect.Parameter.VAR_KEYWORD:
                        params.insert(i, auth_param)
                        params.insert(i + 1, request_param)
                        break
                else:
                    params.append(auth_param)
                    params.append(request_param)

                if operation_mapping:
                    for arg in operation_mapping.args:
                        for i, p in enumerate(params):
                            if p.name == arg.name:
                                params.pop(i)
                                break

                new_sig = inspect.Signature(
                    parameters=params,
                    return_annotation=sig.return_annotation,
                )

                async def wrapped_stub(*args: Any, **kwargs: Any):
                    bound = new_sig.bind(*args, **kwargs)
                    bound.apply_defaults()
                    auth = bound.arguments.pop("__auth__")
                    request: Request = bound.arguments.pop("__request__")
                    mapped_args = {}
                    if operation_mapping:
                        for arg in operation_mapping.args:
                            if arg.source.type == ArgSourceType.BODY:
                                if arg.source.field:
                                    body = await request.json()
                                    mapped_args[arg.name] = body.get(
                                        arg.source.field
                                    )
                                else:
                                    mapped_args[arg.name] = (
                                        await request.body()
                                    )
                            elif arg.source.type == ArgSourceType.QUERY:
                                if arg.source.field:
                                    mapped_args[arg.name] = (
                                        request.query_params.get(
                                            arg.source.field
                                        )
                                    )
                                else:
                                    mapped_args[arg.name] = (
                                        request.query_params
                                    )
                            elif arg.source.type == ArgSourceType.HEADER:
                                if arg.source.field:
                                    mapped_args[arg.name] = (
                                        request.headers.get(arg.source.field)
                                    )
                                else:
                                    mapped_args[arg.name] = request.headers
                            elif arg.source.type == ArgSourceType.PATH:
                                if arg.source.field:
                                    mapped_args[arg.name] = (
                                        request.path_params.get(
                                            arg.source.field
                                        )
                                    )
                                else:
                                    mapped_args[arg.name] = request.path_params
                            elif arg.source.type == ArgSourceType.AUTH:
                                if arg.source.field:
                                    mapped_args[arg.name] = (
                                        DataAccessor.get_field(
                                            auth, arg.source.field
                                        )
                                    )
                                else:
                                    mapped_args[arg.name] = auth

                    bound.arguments.update(mapped_args)
                    converted_args = TypeConverter.convert_args(
                        method, bound.arguments
                    )
                    result = method(**converted_args)
                    return (
                        await result if asyncio.iscoroutine(result) else result
                    )

                wrapped_stub.__name__ = method.__name__
                wrapped_stub.__doc__ = method.__doc__
                setattr(wrapped_stub, "__signature__", new_sig)
                return wrapped_stub

            wrapped_operation = create_wrapped_operation_method(
                operation_method,
                operation_mapping,
                create_auth_validate_method(auth, security_scheme),
            )

            self.router.add_api_route(
                path=path,
                endpoint=wrapped_operation,
                methods=[http_method],
                response_model=get_return_type(operation_method),
                status_code=status_code,
            )

    def _get_operation_mapping(
        self, operation_name: str
    ) -> OperationMapping | None:
        for operation in self.component_mapping.operations:
            if operation.name == operation_name:
                return operation
        return None


class GenericAPI(BaseAPI):
    def __init__(
        self,
        component_mapping: ComponentMapping,
        auth: APIAuth | None = None,
    ):
        super().__init__(component_mapping, auth)
        self.router.add_api_route("/__run__", self.run, methods=["POST"])
        self.router.add_api_route("/__spec__", self.spec, methods=["GET"])

    def run(self, request: RunRequest) -> Any:
        """Run operation."""
        try:
            return self.component_mapping.component.__run__(
                operation=request.operation, context=request.context
            )
        except BaseError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))

    async def spec(self) -> ComponentSpec:
        """Get component spec."""
        component_name = self.component_mapping.component._get_name()
        spec_builder = SpecBuilder()
        spec = spec_builder.build_component_spec(component_name=component_name)
        return spec


class GenericAsyncAPI(BaseAPI):
    def __init__(
        self,
        component_mapping: ComponentMapping,
        auth: APIAuth | None = None,
    ):
        super().__init__(component_mapping, auth)
        self.router.add_api_route("/__run__", self.run, methods=["POST"])
        self.router.add_api_route("/__spec__", self.spec, methods=["GET"])

    async def run(self, request: RunRequest) -> Any:
        """Run operation."""
        try:
            return await self.component_mapping.component.__arun__(
                operation=request.operation,
                context=request.context,
            )
        except BaseError as e:
            raise HTTPException(status_code=e.status_code, detail=str(e))

    async def spec(self) -> ComponentSpec:
        """Get component spec."""
        component_name = self.component_mapping.component._get_name()
        spec_builder = SpecBuilder()
        spec = spec_builder.build_component_spec(component_name=component_name)
        return spec


class Auth:
    api_keys: list[str]

    def __init__(self, api_keys: list[str]):
        self.api_keys = api_keys

    async def authenticate(
        self,
        security_scopes: SecurityScopes,
        token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer()),
    ) -> None:
        if token is not None and token.credentials in self.api_keys:
            return
        raise UnauthenticatedException()


class UnauthenticatedException(HTTPException):
    def __init__(self, detail: str = "Requires authentication"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
