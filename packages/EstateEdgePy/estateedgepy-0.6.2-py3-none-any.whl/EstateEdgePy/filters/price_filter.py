import pyarrow as pa
import pyarrow.compute as pc
from typing import Optional

from EstateEdgePy.filters._base_filter_ import BaseFilter


class PriceRangeFilter(BaseFilter):
    def __init__(
        self,
        column: str,
        set_price: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ):
        self.column = column
        self.set_price = set_price
        self.min_price = min_price
        self.max_price = max_price

    def apply(self, data: pa.Table) -> pa.Table:
        mask = None
        if self.set_price is not None:
            mask = pc.equal(data[self.column], self.set_price)
        if self.min_price is not None:
            mask = pc.greater_equal(data[self.column], self.min_price)
        if self.max_price is not None:
            max_mask = pc.less_equal(data[self.column], self.max_price)
            mask = max_mask if mask is None else pc.and_(mask, max_mask)
        return data.filter(mask) if mask is not None else data