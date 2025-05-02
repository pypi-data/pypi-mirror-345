import pyarrow as pa
from rich import box
from typing import Optional, Union
import pandas as pd
from rich.table import Table

from SanctionSightPy.core._rich_ import repr_rich, df_to_rich_table


class RichArrowTableViewer:
    def __init__(self, arrow_table: Union[pd.DataFrame, pa.Table], title: str = "", title_style: str = "bold"):
        self.arrow_table = arrow_table
        self.title = title
        self.title_style = title_style

    def __rich__(
        self,
        index_name: Optional[str] = None,
        max_rows: int = 20,
        table_box: box.Box = box.SIMPLE_HEAVY,
    ) -> Table:
        """
        Converts the internal pyarrow.Table to a styled Rich Table.

        :param index_name: Optional index name to include
        :param max_rows: Max number of rows to display
        :param table_box: Optional Rich box style
        :return: rich.table.Table instance
        """
        return df_to_rich_table(
            df=self.arrow_table,
            index_name=index_name,
            title=self.title,
            title_style=self.title_style,
            max_rows=max_rows,
            table_box=table_box,
        )

    # def render(self, index_name: Optional[str] = None, max_rows: int = 20):
    #     """
    #     Renders the Rich Table directly to the console.
    #     """
    #     from rich.console import Console
    #     console = Console()
    #     rich_table = self.to_rich_table(index_name=index_name, max_rows=max_rows)
    #     console.print(rich_table)

    def __repr__(self):
        return repr_rich(self.__rich__())
