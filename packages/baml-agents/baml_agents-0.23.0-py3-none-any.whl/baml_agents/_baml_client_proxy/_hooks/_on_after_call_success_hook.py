from abc import ABC, abstractmethod
from typing import final

from baml_agents._baml_client_proxy._hooks._base_hook import (
    BaseBamlHookAsync,
    BaseBamlHookContext,
    BaseBamlHookSync,
)
from baml_agents._baml_client_proxy._hooks._types import Mutable


@final
class OnAfterCallSuccessHookContext(BaseBamlHookContext):
    pass


class OnAfterCallSuccessHookAsync(BaseBamlHookAsync, ABC):
    @abstractmethod
    async def on_after_call_success(
        self,
        *,
        ctx: OnAfterCallSuccessHookContext,
        result: Mutable,
    ) -> None:
        pass


class OnAfterCallSuccessHookSync(BaseBamlHookSync, ABC):
    @abstractmethod
    def on_after_call_success(
        self,
        *,
        ctx: OnAfterCallSuccessHookContext,
        result: Mutable,
    ) -> None:
        pass
