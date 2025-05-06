from collections.abc import Iterator
from functools import partial

from ....utils import (
    APIClient,
    BasicAuth,
    fetch_all_pages,
)
from ..assets import (
    ConfluenceAsset,
)
from .credentials import ConfluenceCredentials
from .endpoints import ConfluenceEndpointFactory
from .pagination import ConfluencePagination

_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


class ConfluenceClient(APIClient):
    def __init__(
        self,
        credentials: ConfluenceCredentials,
    ):
        self.account_id = credentials.account_id
        auth = BasicAuth(
            username=credentials.username, password=credentials.token
        )
        super().__init__(
            auth=auth,
            host=credentials.base_url,
            headers=_HEADERS,
        )

    def pages(self):
        request = partial(
            self._get,
            endpoint=ConfluenceEndpointFactory.pages(),
        )
        yield from fetch_all_pages(request, ConfluencePagination)

    def users(self):
        request_body = {"accountIds": [self.account_id]}
        request = partial(
            self._post,
            endpoint=ConfluenceEndpointFactory.users(),
            data=request_body,
        )
        yield from fetch_all_pages(request, ConfluencePagination)

    def fetch(self, asset: ConfluenceAsset) -> Iterator[dict]:
        """Returns the needed metadata for the queried asset"""
        if asset == ConfluenceAsset.PAGES:
            yield from self.pages()

        elif asset == ConfluenceAsset.USERS:
            yield from self.users()

        else:
            raise ValueError(f"This asset {asset} is unknown")
