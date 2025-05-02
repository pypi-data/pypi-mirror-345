from typing import Optional, Union, List
import pyarrow as pa
import pandas as pd

from EstateEdgePy.core._table_ import RichArrowTableViewer
from EstateEdgePy.filters.base_filter import BaseFilter
from EstateEdgePy.src._client import EstateEdgeClient


class PropertyService:
    """A service class for retrieving and processing property data from EstateEdge.

    This class provides methods to fetch property data, apply filters, and convert
    the data to pandas DataFrames for easier analysis.

    Args:
        client (EstateEdgeClient): An authenticated client for EstateEdge API access.
    """

    def __init__(self, client: EstateEdgeClient) -> None:
        """Initialize the PropertyService with an EstateEdge client.

        Args:
            client: An authenticated EstateEdgeClient instance for API access.
        """
        self.client = client

    async def get_filtered(
            self,
            state: str,
            filters: Optional[List[BaseFilter]] = None
    ) -> RichArrowTableViewer:
        """Retrieve property data for a state with optional filtering.

        Fetches property data from the API and applies the specified filters sequentially.
        Returns the data as a pyarrow Table for efficient processing.

        Args:
            state: The state code (e.g., 'CA') to fetch properties for.
            filters: Optional list of filter objects to apply to the data.

        Returns:
            A pyarrow Table containing the filtered property data.

        Example:
            >>> service = PropertyService(client)
            >>> filters = [PriceFilter(min_price=500000), BedroomsFilter(min_bedrooms=3)]
            >>> filtered_data = await service.get_filtered('CA', filters)
        """
        raw_data = await self.client.get_property_table(state)
        if filters:
            for filter_item in filters:
                raw_data = filter_item.apply(raw_data)
        return RichArrowTableViewer(raw_data)

    async def to_pandas(self, state: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Retrieve property data and convert it to a pandas DataFrame.

        Gets property data for the specified state and optionally selects specific columns.
        This provides a convenient interface for data analysis and manipulation.

        Args:
            state: The state code to fetch properties for.
            columns: Optional list of column names to include in the DataFrame.
                    If None, all columns are included.

        Returns:
            A pandas DataFrame containing the property data.

        Example:
            >>> service = PropertyService(client)
            >>> df = await service.to_pandas('NY', columns=['price', 'bedrooms', 'bathrooms'])
            >>> df.head()
        """
        data = await self.get_filtered(state)
        df = data.to_pandas()
        return df[columns] if columns else df
