from abc import ABC, abstractmethod
from pathlib import Path

from satif_core.types import Datasource, SDIFPath


class Standardizer(ABC):
    @abstractmethod
    def standardize(
        self,
        datasource: Datasource,
        output_path: SDIFPath,
        *,
        overwrite: bool = False,
        **kwargs,
    ) -> Path:
        pass


class AsyncStandardizer(Standardizer, ABC):
    @abstractmethod
    async def standardize(
        self,
        datasource: Datasource,
        output_path: SDIFPath,
        *,
        overwrite: bool = False,
        **kwargs,
    ) -> Path:
        pass
