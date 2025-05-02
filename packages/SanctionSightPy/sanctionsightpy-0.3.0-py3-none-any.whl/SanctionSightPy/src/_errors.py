from typing import Optional, Dict, Union, cast


class SanctionError(Exception):
    def __init__(
            self,
            message: Optional[str] = None,
            headers: Optional[Union[Dict[str, str], None]] = None,
            http_body: Optional[Union[bytes, str, None]] = None,
            status_code: Optional[int] = None,
            error_code: Optional[str] = None,
    ) -> None:
        body: Optional[str] = None
        if http_body and hasattr(http_body, "decode"):
            try:
                body = cast(bytes, http_body).decode("utf-8")
            except BaseException:
                body = "Unable to decode body as utf-8. Please try again"

        self.message = message
        self.status_code = status_code
        self.headers = headers or {}
        self.http_body = body
        self.error_code = error_code
        self.request_id = self.headers.get("X-Request-ID", None)

        super(SanctionError, self).__init__(self._format_message())

    def __str__(self) -> str:
        """
        Return the error message.
        """
        return self._format_message()

    def __repr__(self):
        """
        Return a string representation of the DataDockError instance.
        """
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"status_code={self.status_code}, "
            f"error_code='{self.error_code}', "
            f"headers={self.headers}, "
            f"http_body='{self.http_body}', "
            f"request_id='{self.request_id}')"
        )

    def _format_message(self) -> str:
        """
        Format the error message.

        Returns:
        A formatted string containing the error message, status code, error code, headers, request ID, and HTTP body.
        """
        error_msg = f"\nError Message: {self.message}"
        if self.status_code is not None:
            error_msg += f"\nError Status Code: {self.status_code}"
        if self.error_code is not None:
            error_msg += f"\nError Code Message: {self.error_code}"
        if self.headers:
            error_msg += f"\nHeaders Error: {self.headers}"
        if self.request_id:
            return f"\nRequest ID Error: {self.request_id} {self.message}"
        if self.http_body:
            error_msg += f"\nHTTP Body Error: {self.http_body}"
        return error_msg


class SanctionResponseError(SanctionError):
    def __init__(self, status, message, headers=None, http_body=None, error_code=None):
        super().__init__(message=message, headers=headers, http_body=http_body, status_code=status, error_code=error_code)


class SanctionConnectionError(SanctionError):
    def __init__(self, message, headers=None, http_body=None, status_code=None, error_code=None):
        super().__init__(message=message, headers=headers, http_body=http_body, status_code=status_code, error_code=error_code)


class SanctionServerError(SanctionError):
    def __init__(self, message, headers=None, http_body=None, status_code=None, error_code=None):
        super().__init__(message=message, headers=headers, http_body=http_body, status_code=status_code, error_code=error_code)


# Other error classes can remain the same if they don't need additional attributes
class SanctionTimeoutError(SanctionError):
    def __init__(self, message, headers=None, http_body=None, status_code=None, error_code=None):
        super().__init__(message=message, headers=headers, http_body=http_body, status_code=status_code, error_code=error_code)


class InvalidURLError(SanctionError):
    pass


class ClientPayloadError(SanctionError):
    pass


class TooManyRedirectsError(SanctionError):
    pass


class ContentTypeError(SanctionError):
    pass


class UnexpectedError(SanctionError):
    pass
