import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import urljoin
from uuid import UUID

import httpx as aiohttp
from chatbot.ext.idwall.entities import (
    ErrorResponse,
    PersonalProfile,
    ProfileData,
    ProfileFlow,
    ProfileFlowsResponse,
    ProfileRequest,
    ProfileResponse,
    StartProfileFlowResponse,
)
from chatbot.ext.idwall.exceptions import IdwallAPIError

APITimeoutError = ValueError
from settings import settings

logger = logging.getLogger(__name__)

PROFILE_ALREADY_CREATED_PATTERN = r"^Profile \"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\" already exists$"  # noqa: E501


@dataclass(frozen=True)
class HttpRequestInterface:
    host: str
    path: str
    method: str
    params: Mapping[str, str] = field(default_factory=lambda: {})
    headers: Optional[Dict[str, Any]] = None
    json: Optional[Any] = None


@dataclass(frozen=True)
class HttpResponseInterface:
    status: int
    content: bytes
    headers: Optional[Dict[str, Any]] = None


class IdwallClient:
    def __init__(
        self,
        total_timeout: float = settings.IDWALL_TIMEOUT_S,
    ):
        self.total_timeout = total_timeout

    async def _request(
        self, http_request: HttpRequestInterface
    ) -> HttpResponseInterface:
        timeout = aiohttp.ClientTimeout(
            total=self.total_timeout,
        )
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = urljoin(http_request.host, http_request.path)
                async with session.request(
                    http_request.method,
                    url,
                    headers=http_request.headers,
                    json=http_request.json,
                    params=http_request.params,
                ) as resp:
                    response: aiohttp.ClientResponse = resp
                    content: bytes = await response.content.read()
                    return HttpResponseInterface(
                        status=response.status,
                        content=content,
                        headers=dict(response.headers),
                    )
        except asyncio.TimeoutError:
            raise APITimeoutError(
                "Request to service timed out",
            )
        except aiohttp.ClientConnectorError:
            raise APITimeoutError(
                "Could not establish a connection with the API service",
            )

    def _get_api_headers(self) -> Dict[str, str]:
        return {
            "Authorization": settings.IDWALL_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def create_sdk_profile(
        self, registration_id: UUID, sdk_token: str, cpf: str
    ) -> ProfileResponse:
        req: ProfileRequest = ProfileRequest(
            ref=str(registration_id),
            sdk_token=sdk_token,
            personal=PersonalProfile(
                cpf_number=cpf,
            ),
        )

        rsp: HttpResponseInterface = await self._request(
            http_request=HttpRequestInterface(
                host=settings.IDWALL_BASE_URL,
                path="/maestro/profile/sdk",
                method="POST",
                headers=self._get_api_headers(),
                json=req.model_dump(by_alias=True),
            )
        )

        try:
            if rsp.status >= 200 or rsp.status < 300:
                data = json.loads(rsp.content)
                return ProfileResponse(**data)
            elif rsp.status >= 400 or rsp.status < 500:
                data = json.loads(rsp.content)
                error = ErrorResponse(**data)
                if re.match(PROFILE_ALREADY_CREATED_PATTERN, error.message):
                    return ProfileResponse(data=ProfileData(created=True))

            raise IdwallAPIError(
                status_code=rsp.status,
                message="Unexpected http status code",
                response_body=rsp.content.decode("utf-8"),
            )
        except Exception as e:
            raise IdwallAPIError(
                status_code=rsp.status,
                message=str(e),
                response_body=rsp.content.decode("utf-8"),
            )

    async def _start_flow(
        self, profile_ref: UUID, flow_id: str
    ) -> StartProfileFlowResponse:
        rsp: HttpResponseInterface = await self._request(
            http_request=HttpRequestInterface(
                host=settings.IDWALL_BASE_URL,
                path=f"/maestro/profile/{str(profile_ref)}/flow/{flow_id}",
                method="POST",
                headers=self._get_api_headers(),
            )
        )

        try:
            if rsp.status >= 200 or rsp.status < 300:
                data = json.loads(rsp.content)
                print(data)
                return StartProfileFlowResponse(**data)

            raise IdwallAPIError(
                status_code=rsp.status,
                message="Unexpected http status code",
                response_body=rsp.content.decode("utf-8"),
            )
        except Exception as e:
            raise IdwallAPIError(
                status_code=rsp.status,
                message=str(e),
                response_body=rsp.content.decode("utf-8"),
            )

    async def start_facelink_flow(
        self, registration_id: UUID
    ) -> StartProfileFlowResponse:
        return await self._start_flow(
            profile_ref=registration_id, flow_id=settings.IDWALL_FACELINK_FLOW_ID
        )

    async def start_document_flow(
        self, registration_id: UUID
    ) -> StartProfileFlowResponse:
        return await self._start_flow(
            profile_ref=registration_id, flow_id=settings.IDWALL_DOCUMENT_FLOW_ID
        )

    async def list_flows_exections(
        self, profile_ref: UUID, limit: int = 10
    ) -> List[ProfileFlow]:
        rsp: HttpResponseInterface = await self._request(
            http_request=HttpRequestInterface(
                host=settings.IDWALL_BASE_URL,
                path=f"/maestro/profile/{str(profile_ref)}/profileFlows",
                method="GET",
                headers=self._get_api_headers(),
                params={"limit": str(limit)},
            )
        )

        try:
            if rsp.status >= 200 or rsp.status < 300:
                data = json.loads(rsp.content)
                return ProfileFlowsResponse(**data).data

            raise IdwallAPIError(
                status_code=rsp.status,
                message="Unexpected http status code",
                response_body=rsp.content.decode("utf-8"),
            )
        except Exception as e:
            raise IdwallAPIError(
                status_code=rsp.status,
                message=str(e),
                response_body=rsp.content.decode("utf-8"),
            )
