from spryx_http import SpryxAsyncClient

from spryx_iam.resources.organizations import Organizations
from spryx_iam.resources.plans import Plans


class SpryxIAM(SpryxAsyncClient):
    def __init__(
        self,
        application_id: str,
        application_secret: str,
        base_url: str = "https://api.spryx.ai",
    ):
        super().__init__(
            base_url=base_url,
            application_id=application_id,
            application_secret=application_secret,
        )

        self.organizations = Organizations(self)
        self.plans = Plans(self)
