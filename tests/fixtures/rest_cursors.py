from urllib.parse import urlencode


class AsyncCursor:
    @staticmethod
    async def all(ac, url: str, limit: int = 500, after=lambda d: d) -> list:
        cursor = AsyncCursor(ac, url, limit)
        data = []

        while await cursor.next():
            data.extend(cursor.data)

        return after(data)

    def __init__(self, ac, url: str, limit: int = 500):
        self.ac = ac
        self.url = url
        self.limit = limit
        self.next_page_token = None
        self.has_next_page = True
        self._data = []

    async def next(self) -> bool:
        has_next_page = self.has_next_page

        if has_next_page is True:
            parameters = {"limit": self.limit}
            if not self.next_page_token is None:
                parameters["nextPageToken"] = self.next_page_token

            response = await self.ac.get_json(f"{self.url}?{urlencode(parameters)}")
            body = response.json()

            self.next_page_token = body["nextPageToken"]
            self.limit = body["limit"]
            self._data = body["results"]
            self.has_next_page = len(self._data) == self.limit

        return has_next_page

    @property
    def data(self) -> list:
        return self._data
