from http import HTTPStatus
from typing import List, Optional

from kumoapi.json_serde import to_json_dict
from kumoapi.online_serving import (
    OnlineServingEndpointRequest,
    OnlineServingEndpointResource,
)

from kumoai.client import KumoClient
from kumoai.client.utils import (
    parse_id_response,
    parse_patch_response,
    parse_response,
    raise_on_error,
)

OnlineServingEndpointID = str


class OnlineServingEndpointAPI:
    r"""Typed API definition for Kumo graph definition."""
    def __init__(self, client: KumoClient) -> None:
        self._client = client
        self._base_endpoint = '/online_serving_endpoints'

    def create(self,
               req: OnlineServingEndpointRequest) -> OnlineServingEndpointID:
        resp = self._client._post(self._base_endpoint, json=to_json_dict(req))
        raise_on_error(resp)
        return parse_id_response(resp)

    def get_if_exists(
        self, id: OnlineServingEndpointID
    ) -> Optional[OnlineServingEndpointResource]:
        resp = self._client._get(f'{self._base_endpoint}/{id}')
        if resp.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_on_error(resp)
        return parse_response(OnlineServingEndpointResource, resp)

    def list(self) -> List[OnlineServingEndpointResource]:
        resp = self._client._get(self._base_endpoint)
        raise_on_error(resp)
        return parse_response(List[OnlineServingEndpointResource], resp)

    def update(self, id: OnlineServingEndpointID,
               req: OnlineServingEndpointRequest) -> bool:
        resp = self._client._patch(f'{self._base_endpoint}/{id}',
                                   data=to_json_dict(req))
        raise_on_error(resp)
        return parse_patch_response(resp)

    def delete(self, id: OnlineServingEndpointID) -> None:
        """This is idempotent and can be called multiple times."""
        resp = self._client._delete(f'{self._base_endpoint}/{id}')
        raise_on_error(resp)
