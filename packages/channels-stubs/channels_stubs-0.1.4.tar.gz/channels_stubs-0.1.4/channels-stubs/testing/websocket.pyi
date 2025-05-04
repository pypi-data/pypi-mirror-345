from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    Optional,
    Tuple,
    TypeAlias,
    TypedDict,
    overload,
)

from asgiref.typing import ASGIVersions
from channels.testing.application import ApplicationCommunicator
from channels.utils import _ChannelApplication
from typing_extensions import NotRequired

class _WebsocketTestScope(TypedDict, total=False):
    spec_version: int
    type: Literal["websocket"]
    asgi: ASGIVersions
    http_version: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[Tuple[bytes, bytes]] | None
    client: Optional[Tuple[str, int]]
    server: Optional[Tuple[str, Optional[int]]]
    subprotocols: Iterable[str] | None
    state: NotRequired[Dict[str, Any]]
    extensions: Optional[Dict[str, Dict[object, object]]]

_Connected: TypeAlias = bool
_CloseCodeOrAcceptSubProtocol: TypeAlias = int | str | None
_WebsocketConnectResponse: TypeAlias = Tuple[_Connected, _CloseCodeOrAcceptSubProtocol]

class WebsocketCommunicator(ApplicationCommunicator):
    scope: _WebsocketTestScope
    response_headers: list[tuple[bytes, bytes]] | None

    def __init__(
        self,
        application: _ChannelApplication,
        path: str,
        headers: Iterable[Tuple[bytes, bytes]] | None = ...,
        subprotocols: Iterable[str] | None = ...,
        spec_version: int | None = ...,
    ) -> None: ...
    async def connect(self, timeout: float = ...) -> _WebsocketConnectResponse: ...
    async def send_to(
        self, text_data: str | None = ..., bytes_data: bytes | None = ...
    ) -> None: ...
    @overload
    async def send_json_to(self, data: dict[str, Any]) -> None: ...
    @overload
    async def send_json_to(self, data: Any) -> None: ...
    async def receive_from(self, timeout: float = ...) -> str | bytes: ...
    async def receive_json_from(self, timeout: float = ...) -> dict[str, Any]: ...
    async def disconnect(self, code: int = ..., timeout: float = ...) -> None: ...
