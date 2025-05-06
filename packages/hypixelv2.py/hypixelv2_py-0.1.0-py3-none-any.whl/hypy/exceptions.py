import httpx
from pydantic import BaseModel, ValidationError
from typing import Type

class HypixelAPIError(Exception):
    pass

class HypixelRequestError(HypixelAPIError):
    def __init__(self, response: httpx.RequestError):
        self.response = response
        super().__init__(f"Request failed with status code {response}")

class HypixelHTTPError(HypixelAPIError):
    def __init__(self, response: httpx.Response):
        self.response = response
        super().__init__(f"HTTP error occurred: {response.status_code}: {response.text}")

class HypixelRateLimitError(HypixelHTTPError):
    def __init__(self, response: httpx.Response):
        super().__init__(response)

class HypixelForbiddenError(HypixelHTTPError):
    def __init__(self, response: httpx.Response):
        super().__init__(response)

class HypixelNotFoundError(HypixelAPIError):
    def __init__(self, response: httpx.Response):
        super().__init__(response)

class HypixelValidationError(HypixelAPIError):
    def __init__(self, model: Type[BaseModel], validation_error: ValidationError):
        super().__init__(f"Validation error for model {model.__name__}: {validation_error}")

class HypixelInvalidResponseError(HypixelAPIError):
    pass