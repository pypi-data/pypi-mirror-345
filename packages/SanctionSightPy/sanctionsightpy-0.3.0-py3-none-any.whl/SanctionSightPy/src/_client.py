from aiohttp import (
    ClientResponseError, ClientSession, ClientTimeout,
    TCPConnector, ClientConnectionError, ServerDisconnectedError)
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import pyarrow as pa

from SanctionSightPy.src.logger import CustomLogger
from SanctionSightPy.src._errors import (
    SanctionError,
    SanctionResponseError,
    SanctionConnectionError,
    SanctionServerError,
)
from SanctionSightPy.src.constants import SANCTION_URL, BASE_URL
from SanctionSightPy.src.utils import convert_to_table, normalize_agency


class SanctionClient:
    def __init__(self, timeout: int = 30, max_connections: int = 100) -> None:
        self.base_url: str = BASE_URL
        self._headers: dict = {"Accept": "application/json"}
        self._logger = CustomLogger()
        self._timeout = ClientTimeout(total=timeout)
        self._max_connections = max_connections
        self._connector = None
        self._session = None  # Will be initialized on first use

    async def __aenter__(self):
        """Async context manager support"""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Clean up resources"""
        await self.close()

    async def _get_session(self) -> ClientSession:
        """Get or create a session with connection pooling"""
        if self._session is None or self._session.closed:
            if self._connector is None or self._connector.closed:
                self._connector = TCPConnector(
                    limit=self._max_connections,
                    force_close=True,
                    enable_cleanup_closed=True
                )
            self._session = ClientSession(
                headers=self._headers,
                timeout=self._timeout,
                connector=self._connector,
                trust_env=True
            )
        return self._session

    async def close(self) -> None:
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()

        self._session = None
        self._connector = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(SanctionError),
        reraise=True,
        before_sleep=lambda retry_state: CustomLogger().warning(
            f"Retrying due to: {retry_state.outcome.exception()}"
        )
    )
    async def get_sanction_data(self, agency: str) -> pa.Table:
        """Fetch property dataset with improved error handling and logging"""
        agency = normalize_agency(agency)
        url = f"{self.base_url.rstrip('/')}/{SANCTION_URL.lstrip('/')}"
        session = await self._get_session()

        try:
            async with session.get(url, params={"sanctions_agency": agency}) as response:
                try:
                    response.raise_for_status()
                    # Stream response for memory efficiency with large datasets
                    data: List[Dict[str, Any]] = await response.json()
                    self._logger.info(f"Received {len(data)} records for agency: {agency}")
                    return convert_to_table(data)
                except ClientResponseError as error:
                    self._logger.error(f"Unexpected error: {str(error)}")
                    raise SanctionResponseError(
                        status=error.status,
                        message=error.message,
                        headers=dict(error.headers),
                        http_body=await response.read(),
                        error_code="invalid_agency"
                    ) from error

        except ClientConnectionError as error:
            self._logger.error(f"Unexpected error: {str(error)}")
            raise SanctionConnectionError(
                message=str(error),
                status_code=None,
                error_code="connection_error"
            ) from error
        except ServerDisconnectedError as error:
            self._logger.error(f"Unexpected error: {str(error)}")
            raise SanctionServerError(
                message=str(error),
                status_code=None,
                error_code="timeout_error"
            ) from error
        finally:
            await self.close()
