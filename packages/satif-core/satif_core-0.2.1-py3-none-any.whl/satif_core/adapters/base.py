from abc import ABC, abstractmethod

from satif_core.sdif_db import SDIFDatabase
from satif_core.types import Datasource


class Adapter(ABC):
    @abstractmethod
    def adapt(self, sdif_database: SDIFDatabase) -> Datasource:
        pass
