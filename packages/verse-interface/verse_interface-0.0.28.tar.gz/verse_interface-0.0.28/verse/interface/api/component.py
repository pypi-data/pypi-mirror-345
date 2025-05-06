from verse.core import Component, Response, operation

from ._models import APIAuth, APIInfo, ComponentMapping


class API(Component):
    component: Component | None
    components: list[ComponentMapping]
    auth: APIAuth | None
    host: str
    port: int

    def __init__(
        self,
        component: Component | None = None,
        components: list[ComponentMapping] = [],
        auth: APIAuth | None = None,
        host: str = "127.0.0.1",
        port: int = 8080,
        **kwargs,
    ):
        """Initialize.

        Args:
            component:
                Component to host as API.
            components:
                Multiple components to host in a single API.
            auth:
                Component to handle authentication.
            host:
                Host IP address.
            port:
                HTTP port.
        """
        self.component = component
        self.components = components
        self.auth = auth
        self.host = host
        self.port = port
        super().__init__(**kwargs)

    @operation()
    def run(self) -> Response[None]:
        """Run the API."""
        ...

    @operation()
    def get_info(self) -> Response[APIInfo]:
        """Get API Info"""
        ...
