from datetime import datetime
from typing import List, Dict, Any, Union, Optional
import pyarrow as pa
import pandas as pd

from SanctionSightPy.src._errors import SanctionError


def convert_to_table(data: List[Dict[str, Any]]) -> Union[pd.DataFrame, pa.Table]:
    """Get the properties"""
    if not data:
        raise SanctionError(
            message="""Pass a data value in here.
            Data value is of type list(dict())""", status_code=411, error_code="411"
        )

    data = pa.Table.from_pylist(data)
    return data


def normalize_agency(agency: str) -> str:
    if agency.strip() == "":
        raise SanctionError(message="""
        You are to pass an agency value.
        For example: uk_sanctions""", status_code=411, error_code="411")

    agency = agency.lower().strip()
    if not agency.endswith("_sanctions"):
        agency = f"{agency}_sanctions"
    return agency


def parse_date(date: Optional[Union[str, datetime]]) -> Optional[datetime]:
    if date is None:
        return None
    if isinstance(date, datetime):
        return date

    formats_to_try = ["%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%Y"]  # Try multiple date formats

    for fmt in formats_to_try:
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            continue

    raise SanctionError(f"Date string '{date}' doesn't match any supported formats",
                        status_code=411, error_code="411")
