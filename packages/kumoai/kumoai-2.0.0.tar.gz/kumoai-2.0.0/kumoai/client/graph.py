from http import HTTPStatus
from typing import Any, Dict, Optional

from kumoapi.common import ValidationResponse
from kumoapi.data_snapshot import GraphSnapshotID, GraphSnapshotResource
from kumoapi.graph import (
    EdgeHealthResponse,
    GraphDefinition,
    GraphResource,
    GraphValidationRequest,
)
from kumoapi.json_serde import to_json_dict

from kumoai.client import KumoClient
from kumoai.client.utils import (
    parse_id_response,
    parse_response,
    raise_on_error,
)

GraphID = str


class GraphAPI:
    r"""Typed API definition for Kumo graph definition."""
    def __init__(self, client: KumoClient) -> None:
        self._client = client
        self._base_endpoint = '/graphs'
        self._snapshot_endpoint = '/graphsnapshots'

    def create_graph(
        self,
        graph_def: GraphDefinition,
        *,
        name_alias: Optional[str] = None,
        force_rename: bool = False,
    ) -> GraphID:
        r"""Creates a Graph (metadata definition) resource object in Kumo."""
        params: Dict[str, Any] = {'force_rename': force_rename}
        if name_alias:
            params['name_alias'] = name_alias
        resp = self._client._post(
            self._base_endpoint,
            params=params,
            json=to_json_dict(graph_def),
        )
        raise_on_error(resp)
        return parse_id_response(resp)

    def get_graph_if_exists(
        self,
        graph_id_or_name: str,
    ) -> Optional[GraphResource]:
        resp = self._client._get(f'{self._base_endpoint}/{graph_id_or_name}')
        if resp.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_on_error(resp)
        return parse_response(GraphResource, resp)

    def create_snapshot(
        self,
        graph_id: GraphID,
        *,
        refresh_source: bool = False,
    ) -> GraphSnapshotID:
        params: Dict[str, Any] = {
            'graph_id': graph_id,
            'refresh_source': refresh_source
        }
        resp = self._client._post(self._snapshot_endpoint, params=params)
        raise_on_error(resp)
        return GraphSnapshotID(parse_id_response(resp))

    def get_snapshot(
        self,
        snapshot_id: GraphSnapshotID,
    ) -> GraphSnapshotResource:
        resp = self._client._get(f'{self._snapshot_endpoint}/{snapshot_id}')
        raise_on_error(resp)
        return parse_response(GraphSnapshotResource, resp)

    def get_snapshot_if_exists(
        self,
        snapshot_id: GraphSnapshotID,
    ) -> Optional[GraphSnapshotResource]:
        resp = self._client._get(f'{self._snapshot_endpoint}/{snapshot_id}')
        if resp.status_code == HTTPStatus.NOT_FOUND:
            return None

        raise_on_error(resp)
        return parse_response(GraphSnapshotResource, resp)

    def get_edge_stats(
        self,
        graph_snapshot_id: GraphSnapshotID,
    ) -> EdgeHealthResponse:
        r"""Fetches edge statistics given a snapshot id"""
        resp = self._client._get(
            f'{self._snapshot_endpoint}/edge_health/{graph_snapshot_id}')
        raise_on_error(resp)
        return parse_response(EdgeHealthResponse, resp)

    def validate_graph(
        self,
        request: GraphValidationRequest,
    ) -> ValidationResponse:
        response = self._client._post(f'{self._base_endpoint}/validate',
                                      json=to_json_dict(request))
        raise_on_error(response)
        return parse_response(ValidationResponse, response)

    def infer_links(self, graph: GraphDefinition) -> GraphDefinition:
        resp = self._client._post(f'{self._base_endpoint}/infer_links',
                                  json=to_json_dict(graph))
        raise_on_error(resp)
        return parse_response(GraphDefinition, resp)
