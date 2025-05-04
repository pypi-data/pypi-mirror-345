from typing import List

from spryx_http.base import SpryxAsyncClient

from spryx_iam.types.plan import Plan


class Plans:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client

    async def list(self) -> List[Plan]:
        return await self._client.get(path="/iam/v1/plans")
