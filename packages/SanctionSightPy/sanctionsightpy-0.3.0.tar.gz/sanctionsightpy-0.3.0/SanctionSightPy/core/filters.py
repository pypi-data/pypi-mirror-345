import warnings
import pyarrow as pa
import pyarrow.compute as pc

from SanctionSightPy.src.logger import CustomLogger

warnings.warn(
    "This filters.py module is deprecated and will be removed in a future version.",
    category=DeprecationWarning,
    stacklevel=2
)

logging = CustomLogger().logger


def convert_to_timestamp(date_column: pa.Array) -> pa.Array:
    """Convert a PyArrow string column to timestamps."""
    return pc.strptime(date_column, format="%m-%d-%Y", unit="s")


def parse_date_range(date_input: str) -> tuple:
    """Parse a date range input (e.g., '12-06-2024:12-07-2024') into start and end dates."""
    start_date, end_date = date_input.split(":")
    return start_date.strip() or None, end_date.strip() or None


def filter_by_exact_date(data: pa.Table, date_str: str, column: str) -> pa.Table:
    """Filter a table for an exact sale_date match."""
    sale_date_col = convert_to_timestamp(data[column])
    target_date = pc.strptime(date_str, format="%m-%d-%Y", unit="s")
    return data.filter(pc.equal(sale_date_col, target_date))


def filter_by_date_range(data: pa.Table, date_range: str, column: str) -> pa.Table:
    """Filter a table based on a date range."""
    sale_date_col = convert_to_timestamp(data[column])
    start_date, end_date = parse_date_range(date_range)

    conditions = []
    if start_date:
        start_ts = pc.strptime(start_date, format="%m-%d-%Y", unit="s")
        conditions.append(pc.greater_equal(sale_date_col, start_ts))
    if end_date:
        end_ts = pc.strptime(end_date, format="%m-%d-%Y", unit="s")
        conditions.append(pc.less_equal(sale_date_col, end_ts))

    if conditions:
        mask = conditions[0] if len(conditions) == 1 else pc.and_(*conditions)
        return data.filter(mask)

    return data


def filter_by_date(data: pa.Table, date_input: str, date_column: str) -> pa.Table:
    """Main function to filter PyArrow Table by date (single date or range)."""
    if ":" in date_input:
        return filter_by_date_range(data, date_input, date_column)
    return filter_by_exact_date(data, date_input, date_column)
