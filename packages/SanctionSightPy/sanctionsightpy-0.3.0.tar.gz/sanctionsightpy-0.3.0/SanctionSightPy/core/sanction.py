from typing import Optional, Union, List
import pyarrow as pa
import pandas as pd

from SanctionSightPy.core._table_ import RichArrowTableViewer
from SanctionSightPy.filters.base_filter import BaseFilter
from SanctionSightPy.src._client import SanctionClient


class SanctionService:
    """A service class for retrieving and processing sanction data from SanctionSightPy.

    This class provides methods to fetch sanction data, apply filters, and convert
    the data to pandas DataFrames for easier analysis.

    Args:
        client (SanctionClient): An authenticated client for SanctionClient API access.
    """

    def __init__(self, client: SanctionClient) -> None:
        """Initialize the PropertyService with an EstateEdge client.

        Args:
            client: An authenticated EstateEdgeClient instance for API access.
        """
        self.client = client

    async def get_filtered(
            self,
            agency: str,
            filter_items: Optional[List[BaseFilter]] = None
    ) -> Union[pa.Table, RichArrowTableViewer]:
        """Retrieve property data for a state with optional filtering.

        Fetches property data from the API and applies the specified filters sequentially.
        Returns the data as a pyarrow Table for efficient processing.

        Args:
            agency: The sanction agency code (e.g., 'uk_sanctions') to fetch properties for.
            filter_items: Optional list of filter objects to apply to the data.

        Returns:
            A pyarrow Table containing the filtered property data.

        Example:
            >>> service = SanctionService(client)
            >>> all_filters = [DateRangeFilter(min_price=500000), NameFilter(min_bedrooms=3)]
            >>> filtered_data = await service.get_filtered('canada_sanction', all_filters)
        """
        raw_data = await self.client.get_sanction_data(agency)
        if filter_items:
            for filter_item in filter_items:
                raw_data = filter_item.apply(raw_data)
        return raw_data

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
            >>> service = SanctionService(client)
            >>> df_result = await service.to_pandas('canada_sanction', columns=['entity', 'last_name'])
            >>> df_result.head()
        """
        data = await self.get_filtered(state)
        df = data.to_pandas()
        return df[columns] if columns else df

