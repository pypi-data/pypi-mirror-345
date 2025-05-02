import re
from typing import Union


BASE_URL: str = "https://datadock-api-2-hkf5dhbfdrgbhag4.centralus-01.azurewebsites.net"
DOCS_URL: str = "/api/globalcomply/docs"
SANCTION_URL: str = "/api/v1/globalcomply"

IntString = Union[str, int]
YYYY_MM_DD = "\\d{4}-\\d{2}-\\d{2}"
DATE_PATTERN = re.compile(YYYY_MM_DD)
DATE_RANGE_PATTERN = re.compile(f"({YYYY_MM_DD})?:?(({YYYY_MM_DD})?)?")
