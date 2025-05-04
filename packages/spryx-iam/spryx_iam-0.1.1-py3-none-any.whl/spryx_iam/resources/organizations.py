from spryx_core import Page
from spryx_http.base import SpryxAsyncClient

from spryx_iam.types.organization import Organization


class Organizations:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client

    async def retrieve(self, organization_id: str) -> Organization:
        if not organization_id:
            raise ValueError(
                f"Expected a non-empty value for `organization_id` but received {organization_id!r}"
            )

        return await self._client.get(
            path=f"/iam/v1/organizations/{organization_id}", cast_to=Organization
        )

    async def list(self) -> Page[Organization]:
        return await self._client.get(path="/iam/v1/organizations")
