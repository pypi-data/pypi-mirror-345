from typing import Iterable, Literal

import grpc

from . import beaker_pb2 as pb2
from ._service_client import RpcMethod, ServiceClient
from .exceptions import *
from .types import *


class SecretClient(ServiceClient):
    def get(self, name: str, *, workspace: pb2.Workspace | None = None) -> pb2.Secret:
        return self.rpc_request(
            RpcMethod[pb2.GetSecretResponse](self.service.GetSecret),
            pb2.GetSecretRequest(
                workspace_id=self.resolve_workspace_id(workspace),
                secret_name=name,
            ),
            exceptions_for_status={grpc.StatusCode.NOT_FOUND: BeakerSecretNotFound(name)},
        ).secret

    def read(self, secret: pb2.Secret, *, workspace: pb2.Workspace | None = None) -> str:
        workspace_id = self.resolve_workspace_id(workspace)
        return self.http_request(
            f"workspaces/{workspace_id}/secrets/{self._url_quote(secret.name)}/value",
            method="GET",
        ).content.decode()

    def write(self, name: str, value: str, *, workspace: pb2.Workspace | None = None) -> pb2.Secret:
        workspace_id = self.resolve_workspace_id(workspace)
        self.http_request(
            f"workspaces/{workspace_id}/secrets/{self._url_quote(name)}/value",
            method="PUT",
            data=value.encode(),
        )
        return self.get(name, workspace=workspace)

    def delete(self, secret: pb2.Secret, *, workspace: pb2.Workspace | None = None):
        workspace_id = self.resolve_workspace_id(workspace)
        self.http_request(
            f"workspaces/{workspace_id}/secrets/{self._url_quote(secret.name)}",
            method="DELETE",
            exceptions_for_status={404: BeakerSecretNotFound(secret)},
        )

    def list(
        self,
        *,
        workspace: pb2.Workspace | None = None,
        sort_order: BeakerSortOrder | None = None,
        sort_field: Literal["created", "name"] = "name",
        limit: int | None = None,
    ) -> Iterable[pb2.Secret]:
        if limit is not None and limit <= 0:
            raise ValueError("'limit' must be a positive integer")

        count = 0
        for response in self.rpc_paged_request(
            RpcMethod[pb2.ListSecretsResponse](self.service.ListSecrets),
            pb2.ListSecretsRequest(
                options=pb2.ListSecretsRequest.Opts(
                    sort_clause=pb2.ListSecretsRequest.Opts.SortClause(
                        sort_order=None if sort_order is None else sort_order.as_pb2(),
                        created={} if sort_field == "created" else None,
                        name={} if sort_field == "name" else None,
                    ),
                    workspace_id=self.resolve_workspace_id(workspace),
                    page_size=self.MAX_PAGE_SIZE
                    if limit is None
                    else min(self.MAX_PAGE_SIZE, limit),
                )
            ),
        ):
            for secret in response.secrets:
                count += 1
                yield secret
                if limit is not None and count >= limit:
                    return
