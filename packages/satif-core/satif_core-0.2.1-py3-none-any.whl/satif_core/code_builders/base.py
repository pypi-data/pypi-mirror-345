from abc import ABC, abstractmethod


class CodeBuilder(ABC):
    @abstractmethod
    def build(self, **kwargs) -> str: ...


class AsyncCodeBuilder(CodeBuilder):
    @abstractmethod
    async def build(self, **kwargs) -> str: ...
