import json
import httpx
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, Optional, Any, Dict
from hypy.exceptions import (
    HypixelAPIError,
    HypixelRequestError,
    HypixelHTTPError,
    HypixelRateLimitError,
    HypixelForbiddenError,
    HypixelNotFoundError,
    HypixelValidationError,
    HypixelInvalidResponseError
)
from hypy.modals import (
    BazzarResponse,
    ProfileResponse,
    ProfilesResponse,
    MuseumResponse,
    GardenResponse,
    BingoResponse,
    FireSalesResponse
)

T = TypeVar('T', bound=BaseModel)

class Hypy:
    URL = "https://api.hypixel.net/v2/"
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self._client = httpx.Client(headers={"Api-Key": self.api_key})
        self.headers = {
            "API-Key": self.api_key
        }

    def close(self):
        self._client.close()

    def _make_request(self, endpoint: str, model: Optional[Type[T]], params: Optional[Dict[str, Any]] = None, requires_auth: bool = True) -> T | Dict[str, Any]:
        full_url = self.URL + endpoint.lstrip("/")
        current_headers = self.headers if requires_auth else None
        try:
            response = self._client.get(full_url, params=params, headers=current_headers)
            if response.status_code == 429:
                raise HypixelRateLimitError(response)
            if response.status_code == 403:
                raise HypixelForbiddenError(response)
            if response.status_code == 404:
                raise HypixelNotFoundError(response)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                cause = data.get("cause", "Unknown error")
                raise HypixelInvalidResponseError(f"API request was not successful: {cause}")
            if model:
                try:
                    return model.model_validate(data)
                except ValidationError as e:
                    raise HypixelValidationError(model, e) from e
            else:
                return data

        except httpx.RequestError as e:
            raise HypixelRequestError(e) from e
        except httpx.HTTPStatusError as e:
            raise HypixelHTTPError(e.response) from e
        except json.JSONDecodeError as e:
            raise HypixelInvalidResponseError(f"Failed to decode JSON response: {e}") from e
        except HypixelAPIError:
            raise
        except Exception as e:
            raise HypixelAPIError(f"An unexpected error occurred: {e}") from e

    def bazzar(self) -> BazzarResponse:
        return self._make_request(endpoint="skyblock/bazzar", model=BazzarResponse, requires_auth=False)

    def profile(self, profile_uuid: str) -> ProfileResponse:
        return self._make_request(endpoint="skyblock/profile", model=ProfileResponse, requires_auth=True, params={"profile": profile_uuid})

    def profiles(self, player_uuid: str):
        return self._make_request(endpoint="skyblock/profiles", model=ProfilesResponse, requires_auth=True, params={"uuid": player_uuid})

    def museum(self, profile_uuid: str):
        return self._make_request(endpoint="skyblock/museum", model=MuseumResponse, requires_auth=True, params={"profile": profile_uuid})

    def garden(self, profile_uuid: str):
        return self._make_request(endpoint="skyblock/garden", model=GardenResponse, requires_auth=True, params={"profile": profile_uuid})

    def bingo(self, player_uuid: str):
        return self._make_request(endpoint="skyblock/bingo", model=BingoResponse, requires_auth=True, params={"uuid": player_uuid})

    def firesale(self):
        return self._make_request(endpoint="skyblock/firesales", model=FireSalesResponse, requires_auth=False)


