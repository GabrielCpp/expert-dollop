from urllib.parse import urlencode
from typing import List, Type
from pydantic import BaseModel


class AsyncCursor:
    @staticmethod
    async def all(
        ac,
        url: str,
        unwrap_with: Type[BaseModel],
        limit: int = 500,
        after=lambda d: d,
    ) -> List[BaseModel]:
        cursor = AsyncCursor(ac, url, unwrap_with, limit)
        data = []

        while await cursor.next():
            data.extend(cursor.data)

        return after(data)

    def __init__(self, ac, url: str, unwrap_with: Type[BaseModel], limit: int = 500):
        self.ac = ac
        self.url = url
        self.limit = limit
        self.unwrap_with = unwrap_with
        self.next_page_token = None
        self.has_next_page = True
        self._data = []

    async def next(self) -> bool:
        has_next_page = self.has_next_page

        if has_next_page is True:
            parameters = {"limit": self.limit}
            if not self.next_page_token is None:
                parameters["nextPageToken"] = self.next_page_token

            page = await self.ac.get_json(
                f"{self.url}?{urlencode(parameters)}",
                unwrap_with=self.unwrap_with,
            )
            self.next_page_token = page.next_page_token
            self.limit = page.limit
            self._data = page.results
            self.has_next_page = len(self._data) == self.limit

        return has_next_page

    @property
    def data(self) -> list:
        return self._data
