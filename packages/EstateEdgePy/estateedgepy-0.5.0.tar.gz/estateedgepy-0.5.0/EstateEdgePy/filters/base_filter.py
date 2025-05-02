from abc import ABC, abstractmethod
import pyarrow as pa


class BaseFilter(ABC):
    @abstractmethod
    def apply(self, data: pa.Table) -> pa.Table:
        pass