from typing import Iterable, Literal

import grpc

from . import beaker_pb2 as pb2
from ._service_client import RpcMethod, ServiceClient
from .exceptions import *
from .types import *


class ImageClient(ServiceClient):
    def get(self, image: str) -> pb2.Image:
        return self.rpc_request(
            RpcMethod[pb2.GetImageResponse](self.service.GetImage),
            pb2.GetImageRequest(image_id=self.resolve_image_id(image)),
            exceptions_for_status={grpc.StatusCode.NOT_FOUND: BeakerImageNotFound(image)},
        ).image

    def update(
        self, image: pb2.Image, name: str | None = None, description: str | None = None
    ) -> pb2.Image:
        return self.rpc_request(
            RpcMethod[pb2.UpdateImageResponse](self.service.UpdateImage),
            pb2.UpdateImageRequest(
                image_id=self.resolve_image_id(image), name=name, description=description
            ),
        ).image

    def delete(self, *images: pb2.Image):
        self.rpc_request(
            RpcMethod[pb2.DeleteImagesResponse](self.service.DeleteImages),
            pb2.DeleteImagesRequest(image_ids=[self.resolve_image_id(image) for image in images]),
        )

    def list(
        self,
        *,
        org: pb2.Organization | None = None,
        author: pb2.User | None = None,
        workspace: pb2.Workspace | None = None,
        name_or_description: str | None = None,
        sort_order: BeakerSortOrder | None = None,
        sort_field: Literal["created", "name"] = "name",
        limit: int | None = None,
    ) -> Iterable[pb2.Image]:
        if limit is not None and limit <= 0:
            raise ValueError("'limit' must be a positive integer")

        count = 0
        for response in self.rpc_paged_request(
            RpcMethod[pb2.ListImagesResponse](self.service.ListImages),
            pb2.ListImagesRequest(
                options=pb2.ListImagesRequest.Opts(
                    sort_clause=pb2.ListImagesRequest.Opts.SortClause(
                        sort_order=None if sort_order is None else sort_order.as_pb2(),
                        created={} if sort_field == "created" else None,
                        name={} if sort_field == "name" else None,
                    ),
                    image_name_or_description=name_or_description,
                    organization_id=self.resolve_org_id(org),
                    author_id=None if author is None else self.resolve_user_id(author),
                    workspace_id=None
                    if workspace is None
                    else self.resolve_workspace_id(workspace),
                    page_size=self.MAX_PAGE_SIZE
                    if limit is None
                    else min(self.MAX_PAGE_SIZE, limit),
                )
            ),
        ):
            for image in response.images:
                count += 1
                yield image
                if limit is not None and count >= limit:
                    return

    def url(self, image: pb2.Image) -> str:
        image_id = self.resolve_image_id(image)
        return f"{self.config.agent_address}/im/{self._url_quote(image_id)}"
