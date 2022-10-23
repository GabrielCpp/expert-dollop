from typing import Optional, Type, Callable, List
from pydantic import BaseModel, parse_obj_as
from async_asgi_testclient.response import Response as ClientResponse
from async_asgi_testclient import TestClient
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from .fake_db_helpers import DbFixtureHelper
from .factories import SuperUser
from .object_dump_helpers import jsonify


class IntegratedTestClient(TestClient):
    def __init__(
        self,
        app,
        auth_service: AuthService,
        user_service: Repository[User],
        db_helper: DbFixtureHelper,
    ):
        TestClient.__init__(self, app)
        self.auth_service = auth_service
        self.db_helper = db_helper
        self.user_service = user_service
        self.json_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def login(self, user: User):
        token = self.auth_service.make_token(user.oauth_id)
        self.headers.update({"Authorization": f"Bearer {token}"})

    async def login_super_user(self):
        if self.db_helper.db is None:
            await self.db_helper.load_fixtures(SuperUser())

        user = self.db_helper.db.get_only_one_matching(
            User, lambda u: u.oauth_id == SuperUser.oauth_id
        )

        if user is None:
            raise Exception("You must load SuperUser fixture")

        self.login(user)

    async def post_json(
        self,
        url: str,
        data: Optional[BaseModel] = None,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        params = self._json_request_params(data)
        response = await self.post(url, **params)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def put_json(
        self,
        url: str,
        data: Optional[BaseModel] = None,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        params = self._json_request_params(data)
        response = await self.put(url, **params)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def patch_json(
        self,
        url: str,
        data: Optional[BaseModel] = None,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        params = self._json_request_params(data)
        response = await self.patch(url, **params)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def get_json(
        self,
        url: str,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        response = await self.get(url, headers=self.json_headers)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def delete_json(
        self,
        url: str,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        response = await self.delete(url, headers=self.json_headers)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    def _convert_response(
        self,
        response,
        unwrap_with,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        if unwrap_with is None:
            return response

        result = parse_obj_as(unwrap_with, response.json())

        if callable(after):
            after(result)

        return result

    def _json_request_params(
        self,
        data: Optional[BaseModel] = None,
    ) -> dict:
        params = dict(headers=self.json_headers)

        if not data is None:
            params["data"] = jsonify(data)

        return params
