from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Union

from satif_core.sdif_db import SDIFDatabase
from satif_core.types import SDIFPath


class Transformer(ABC):
    @abstractmethod
    def transform(
        self, sdif: Union[SDIFPath, List[SDIFPath]] | SDIFDatabase
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _export_data(
        self,
        data: Dict[str, Any],
        output_path: Union[str, Path] = Path("."),
        zip_archive: bool = False,
    ) -> Path:
        pass

    def export(
        self,
        sdif: Union[SDIFPath, List[SDIFPath]] | SDIFDatabase,
        output_path: Union[str, Path] = Path("."),
        zip_archive: bool = False,
    ) -> Path:
        transformed_data = self.transform(sdif)
        return self._export_data(
            data=transformed_data, output_path=output_path, zip_archive=zip_archive
        )
