from asyncio import BaseEventLoop
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from asgiref.sync import SyncToAsync
from typing_extensions import ParamSpec

_P = ParamSpec("_P")
_R = TypeVar("_R")

class DatabaseSyncToAsync(SyncToAsync[_P, _R]):
    def thread_handler(self, loop: BaseEventLoop, *args: Any, **kwargs: Any) -> Any: ...

def database_sync_to_async(
    func: Callable[_P, _R],
) -> Callable[_P, Coroutine[Any, Any, _R]]: ...
async def aclose_old_connections() -> None: ...
