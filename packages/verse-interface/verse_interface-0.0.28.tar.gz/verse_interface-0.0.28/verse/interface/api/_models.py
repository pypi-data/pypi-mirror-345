from enum import Enum

from verse.core import Component, DataModel


class APIInfo(DataModel):
    """API Info.

    Attributes:
        host: Host address.
        port: Host port.
        ssl: SSL enabled.
    """

    host: str
    port: int | None
    ssl: bool = False


class APIAuthType(str, Enum):
    """API Auth Type Enum.

    Attributes:
        API_KEY: API Key authentication.
        BEARER_TOKEN: Bearer token (JWT) authentication.
        BASIC: Basic authentication.
    """

    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"


class APIKeyAuthConfig(DataModel):
    """API Key Auth Config.

    Attributes:
        header: Header name for API key.
        query: Query parameter name for API key.
    """

    header: str | None = None
    query: str | None = None


class APIAuth(DataModel):
    """Auth Mapping Info.

    Attributes:
        type: Auth type.
        component: Auth component.
        config: Additional config for auth.
    """

    type: APIAuthType
    component: Component | None = None
    config: APIKeyAuthConfig | None = None


class ArgSourceType(str, Enum):
    """Arg Source Type Enum.

    Attributes:
        BODY: Field from request body.
        QUERY: Field from query parameters.
        HEADER: Field from request headers.
        PATH: Field from URL path.
        AUTH: Field from info.
    """

    BODY = "body"
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    AUTH = "auth"


class ArgSource(DataModel):
    """Argument Source.

    Attributes:
        type: Source type.
        field: Field name for the source.
    """

    type: ArgSourceType
    field: str | None = None


class ArgMapping(DataModel):
    """Argument Mapping Info.

    Attributes:
        name:
            Argument name.
        source:
            Argument source.
    """

    name: str
    source: ArgSource


class OperationMapping(DataModel):
    """Operation Mapping Info.

    Attributes:
        name: Operation name.
        path: URL path.
        method: Http method.
        status_code: Status code.
        args: Arg mappings.
        auth: Auth component.
    """

    name: str
    path: str | None = None
    method: str = "POST"
    status_code: int | None = None
    args: list[ArgMapping] = []
    auth: APIAuth | None = None


class ComponentMapping(DataModel):
    """Component Mapping Info.

    Attributes:
        component: Component.
        prefix: URL prefix.
        operations: Operation mappings.
        auth: Auth component.
    """

    component: Component
    prefix: str = ""
    operations: list[OperationMapping] = []
    auth: APIAuth | None = None
