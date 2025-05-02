import asyncio
import base64
import datetime
import pathlib
import uuid
from typing import Optional, Union

import aiohttp
from ambient_backend_api_client import (
    ApiClient,
    Configuration,
    DeviceAuthorizationRequest,
)
from ambient_backend_api_client import JWTClaims as _JWTClaims
from ambient_backend_api_client import NodeOutput as Node
from ambient_backend_api_client import (
    NodesApi,
    TokenRequest,
    TokenResponse,
)
from async_lru import alru_cache
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import NameOID
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from result import Err, Ok, Result

from ambient_client_common.repositories import backend_api_repo
from ambient_client_common.utils import logger
from ambient_client_common.utils.consistent_hash import consistent_hash
from ambient_edge_server.config import settings
from ambient_edge_server.models.sql_models import (
    SQLAPIUser,
    SQLDeviceAuthRequest,
    SQLToken,
)
from ambient_edge_server.repos.device_auth_repo import SQLDeviceAuthRepository
from ambient_edge_server.repos.node_repo import NodeRepo
from ambient_edge_server.repos.token_repo import TokenRepository


class JWTClaims(_JWTClaims):
    aud: Optional[str] = None


header_scheme = APIKeyHeader(name="Authorization", auto_error=False)


class AuthorizationService:
    def __init__(
        self,
        token_repo: TokenRepository,
        node_repo: NodeRepo,
        device_auth_repo: SQLDeviceAuthRepository,
    ) -> None:
        self.token_repo = token_repo
        self.node_repo = node_repo
        self.device_auth_repo = device_auth_repo
        self._node_id = None

    async def authenticate_backend_token(
        self, token: str = Depends(header_scheme)
    ) -> dict:
        """Authenticate the backend token.

        Args:
            token (str, optional): API JWT. Defaults to Depends(header_scheme).

        Raises:
            HTTPException: If the token is invalid or expired.

        Returns:
            dict: decoded token claims
        """
        try:
            token_claims = await backend_api_repo.decode_token(token)
            return token_claims
        except Exception as e:
            err_msg = f"Error decoding token: {e}"
            logger.error(err_msg)
            raise HTTPException(status_code=401, detail=err_msg)

    async def authenticate(self, token: str = Depends(header_scheme)) -> str:
        """Authenticate the API token.

        Args:
            token (str, optional): Local API Basic Token. Defaults to
                Depends(header_scheme).

        Raises:
            HTTPException: If the token is invalid or expired.

        Returns:
            str: username of the authenticated user
        """
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if token.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Bearer authentication not supported"
            )

        if token.startswith("Basic "):
            token = token[6:]
            decoded_token = base64.b64decode(token).decode("utf-8")
            username, password = decoded_token.split(":", 1)
            if not username or not password:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            api_user = await self.device_auth_repo.get_api_user(username=username)
            if not api_user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            if consistent_hash(password) != api_user.password_hash:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return api_user.username

        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    async def get_auth_headers(self) -> dict:
        token = await self.get_token()
        if not token:
            raise HTTPException(status_code=401, detail="No access token found")
        return {"Authorization": f"Bearer {token}"}

    async def add_local_api_user(self, claims: dict) -> dict:
        username = claims.get("sub")
        password = str(uuid.uuid4())
        await self.device_auth_repo.save_api_user(
            SQLAPIUser(
                username=username,
                password_hash=consistent_hash(password),
            )
        )
        return {
            "username": username,
            "password": password,
        }

    @alru_cache(maxsize=1, ttl=5)
    async def get_token(self) -> Union[str, None]:
        return await self.get_token_uncached()

    async def get_token_uncached(self) -> Union[str, None]:
        logger.info("getting token ...")
        if not self.node_id:
            if not self.node_repo.get_node_id():
                logger.debug("node_id not found, fetching node ...")
                result = await self.fetch_node(refresh=True)
                logger.debug("result: {}", result)
                if result.is_err():
                    logger.error("Error fetching node: {}", result.unwrap_err())
                    return None
                self.node_id = result.unwrap().id
        logger.debug("node_id: {}", self.node_id)
        token_record = await self.device_auth_repo.get_token()
        if token_record:
            logger.debug("Token found in device auth repo")
            if token_record.expires_at > datetime.datetime.now():
                logger.debug("Token found in device auth repo")
                return token_record.access_token
            logger.debug("Token expired, refreshing ...")
            await self.refresh_token()
        logger.debug("Fetching latest token from device auth repo")
        token_record = await self.device_auth_repo.get_token()
        if not token_record:
            logger.error("No token found in device auth repo")
            return None
        logger.debug("Token found in device auth repo")
        return token_record.access_token if token_record else None

    async def verify_authorization_status(self) -> Result[str, str]:
        logger.info("verifying authorization status ...")
        if not self.token_repo.get_access_token():
            logger.error("No access token found in token repo")
            return Err("No access token found in token repo")
        return await self.test_authorization()

    async def fetch_node(self, refresh: bool = False) -> Result[Node, str]:
        if not refresh:
            node = await self.node_repo.get_node_data()
            if node:
                logger.debug("node: {}", node.model_dump_json(indent=4))
                return Ok(node)
        node_id = await self.node_repo.get_node_id()
        if not node_id:
            return Err("Node not found")
        logger.info("fetching node {} ...", node_id)
        try:
            async with ApiClient(self.api_config) as api_client:
                nodes_api = NodesApi(api_client)
                logger.debug("node_id: {}", node_id)
                if not node_id:
                    return Err("Node ID not found")
                node = await nodes_api.get_node_nodes_node_id_get(node_id=int(node_id))
                logger.debug("node: {}", node.model_dump_json(indent=4))
                await self.node_repo.save_node_data(node=node)
                self.node_id = node.id
                return Ok(node)
        except Exception as e:
            err_msg = f"Error fetching node: {e}"
            logger.error(err_msg)
            return Err(err_msg)

    async def request_device_authorization(self) -> DeviceAuthorizationRequest:
        logger.info("requesting device authorization ...")
        try:
            async with aiohttp.ClientSession() as session:
                url = settings.backend_api_url
                async with session.post(
                    f"{url}/oauth/device_authorization"
                ) as response:
                    response.raise_for_status()
                    await self.device_auth_repo.delete_device_auth_request()
                    device_auth_request = DeviceAuthorizationRequest.model_validate(
                        await response.json()
                    )
                    logger.debug(
                        "device_auth_request: {}",
                        device_auth_request.model_dump_json(indent=4),
                    )
                    await self.device_auth_repo.save_device_auth_request(
                        SQLDeviceAuthRequest(
                            device_code=device_auth_request.device_code,
                            user_code=device_auth_request.user_code,
                            verification_uri=device_auth_request.verification_uri,
                            expires_at=datetime.datetime.now()
                            + datetime.timedelta(
                                seconds=device_auth_request.expires_in
                            ),
                        )
                    )
                    return device_auth_request
        except Exception as e:
            err_msg = f"Error requesting device authorization: {e}"
            logger.error(err_msg)
            raise e

    async def authorize_node(self) -> None:
        try:
            logger.info("authorizing node ...")
            device_auth_request = await self.device_auth_repo.get_device_auth_request()
            if not device_auth_request:
                logger.error("No device authorization request found")
                return
            logger.debug("device_auth_request: {}", device_auth_request)
            try:
                device_code = device_auth_request.device_code
                user_code = device_auth_request.user_code
            except Exception as e:
                err_msg = (
                    f"Error getting device authorization request: {e}"
                    f"\n{e.__traceback__.tb_frame.f_code.co_filename}:"
                    f"{e.__traceback__.tb_lineno}"
                    f"\ndir(device_auth_request)={dir(device_auth_request)}"
                )
                logger.error(err_msg)
                return
            logger.info("device code: {}, user code: {}", device_code, user_code)
            request = TokenRequest(
                grant_type="device_authorization",
                token_description=f"node-token-{device_code}",
                request_type="node",
                device_code=device_code,
                user_code=user_code,
            )
            data = request.model_dump(exclude_none=True)
            logger.debug("TokenRequest: {}", data)
            token_response = None
            if device_auth_request.expires_at < datetime.datetime.now():
                logger.error("Device authorization request expired")
                return

            while device_auth_request.expires_at > datetime.datetime.now():
                logger.debug("Calling token endpoint ...")
                try:
                    text = None
                    resp_data = None
                    async with aiohttp.ClientSession() as session:
                        url = settings.backend_api_url
                        async with session.post(
                            f"{url}/oauth/token",
                            json=data,
                        ) as response:
                            text = await response.text()
                            resp_data = await response.json()
                            response.raise_for_status()
                            token_response = TokenResponse.model_validate(resp_data)
                            logger.debug(
                                "token_response: {}",
                                token_response.model_dump_json(indent=4),
                            )
                            break
                except aiohttp.ClientResponseError as e:
                    if e.status == 400:
                        logger.debug("Bad request: {}", text)
                        await asyncio.sleep(5)
                        continue
                    if e.status == 422:
                        logger.debug("Unprocessable entity: {}", resp_data or text)
                        await asyncio.sleep(5)
                        return
                    else:
                        err_msg = f"Error authorizing node: {e}"
                        logger.error(err_msg)
                        return
                except Exception as e:
                    err_msg = f"Error authorizing node: {e}"
                    logger.error(err_msg)
                    return

            if not token_response:
                logger.error("Failed to get token")
                return

            claims = await self.decode_token(token_response.access_token)
            if claims.is_err():
                logger.error("Failed to get claims: {}", claims.unwrap_err())
                return

            node_id = claims.unwrap().sub.split("-")[-1]
            if not node_id:
                logger.error("Failed to get node ID from claims")
                return

            await self.get_and_save_node_data(
                node_id=int(node_id), token=token_response.access_token
            )
            logger.info("Node data saved.")

            await self.device_auth_repo.delete_device_auth_request()
            logger.info("Device authorization request deleted.")
            await self.device_auth_repo.save_token(
                SQLToken(
                    access_token=token_response.access_token,
                    refresh_token=token_response.refresh_token,
                    expires_at=token_response.expires_at,
                )
            )
            logger.info("Token saved.")
        except Exception as e:
            err_msg = f"Error authorizing node: {e}"
            logger.error(err_msg)
            return

    async def decode_token(self, token: str) -> Result[JWTClaims, str]:
        logger.info("fetching whoami ...")
        try:
            async with aiohttp.ClientSession() as session:
                url = settings.backend_api_url
                headers = {"Authorization": f"Bearer {token}"}
                resp_text: Optional[str] = None
                resp_data: Optional[str] = None
                async with session.post(
                    f"{url}/oauth/decode", headers=headers
                ) as response:
                    resp_text = await response.text()
                    resp_data = await response.json()
                    response.raise_for_status()
                    claims = JWTClaims.model_validate(resp_data)
                    logger.debug("claims: {}", claims.model_dump_json(indent=4))
                    return Ok(claims)
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                return Err("Unauthorized" + f": {resp_text}" if resp_text else "")
            else:
                err_msg = f"Error fetching whoami: {e}"
                logger.error(err_msg)
                return Err(err_msg)
        except Exception as e:
            err_msg = f"Error fetching whoami: {e}"
            logger.error(err_msg)
            return Err(err_msg)

    async def get_and_save_node_data(
        self, node_id: int, token: str = ""
    ) -> Result[Node, str]:
        logger.info("fetching node {} ...", node_id)
        try:
            async with aiohttp.ClientSession() as session:
                url = settings.backend_api_url
                if not token:
                    token = await self.get_token()
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(
                    f"{url}/nodes/{node_id}", headers=headers
                ) as response:
                    response.raise_for_status()
                    node = Node.model_validate(await response.json())
                    logger.debug("node: {}", node.model_dump_json(indent=4))
                    await self.node_repo.save_node_data(node=node)
                    self.node_id = node.id
                    return Ok(node)
        except Exception as e:
            err_msg = f"Error fetching node: {e}"
            logger.error(err_msg)
            return Err(err_msg)

    async def refresh_token(self) -> Result[None, str]:
        logger.info("refreshing token ...")
        token_record = await self.device_auth_repo.get_token()
        if not token_record:
            logger.error("No token found in device auth repo")
            return Err("No token found in device auth repo")
        refresh_token = token_record.refresh_token
        logger.debug("refresh_token: {}", refresh_token)
        logger.debug("node_id: {}", self.node_id)

        request_url = f"{settings.backend_api_url}/oauth/token"
        logger.debug("request_url: {}", request_url)

        request = build_refresh_token_request(
            node_id=self.node_id, refresh_token=refresh_token
        )
        data = request.model_dump(exclude_none=True)
        logger.debug("TokenRequest: {}", data)

        resp_text: Optional[str] = None
        async with aiohttp.ClientSession() as session:
            async with session.post(request_url, json=data) as response:
                try:
                    resp_text = await response.text()
                    response.raise_for_status()
                    token_response = TokenResponse.model_validate(await response.json())
                    logger.debug(
                        "token_response: {}", token_response.model_dump_json(indent=4)
                    )
                    await self.device_auth_repo.save_token(
                        SQLToken(
                            access_token=token_response.access_token,
                            refresh_token=token_response.refresh_token,
                            expires_at=token_response.expires_at,
                        )
                    )
                    logger.info("Token refreshed and saved")
                    return Ok(None)
                except aiohttp.ClientResponseError as e:
                    logger.error(f"Failed to refresh token: {e}")
                    logger.error(f"response: {resp_text}")
                    return Err(f"Failed to refresh token: {e}")
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    logger.error(f"response: {resp_text}")
                    return Err(f"Failed to refresh token: {e}")

    async def create_new_refresh_token(self) -> Result[str, str]:
        logger.info("creating refresh token ...")
        node_data = await self.node_repo.get_node_data()
        resp_text: Optional[str] = None
        try:
            headers = {"Authorization": f"Bearer {await self.get_token()}"}
            logger.debug("headers: {}", headers)
            url = settings.backend_api_url
            data = {
                "token_type": "refresh",
                "duration": 3600,
                "user_id": node_data.user_id,
                "org_id": node_data.org_id,
                "node_id": node_data.id,
                "request_type": "node_refresh_token",
            }
            logger.debug("data: {}", data)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{url}/auth/token-mgmt/", headers=headers, data=data
                ) as response:
                    resp_text = await response.text()
                    logger.debug("response: {}", resp_text)
                    response.raise_for_status()
                    token_response = TokenResponse.model_validate(await response.json())
                    logger.debug(
                        "token_response: {}", token_response.model_dump_json(indent=4)
                    )
                    self.token_repo.save_access_token(token_response.access_token)
                    self.token_repo.save_refresh_token(token_response.refresh_token)
                    return Ok("Refresh token created")
        except Exception as e:
            err_msg = f"Failed to create refresh token: {e}"
            if resp_text:
                err_msg += f"\nresponse: {resp_text}"
            logger.error(err_msg)
            return Err(err_msg)

    async def test_authorization(self) -> Result[str, str]:
        logger.info("testing authorization ...")
        try:
            logger.info("pinging backend ...")
            async with aiohttp.ClientSession() as session:
                url = settings.backend_api_url
                headers = {"Authorization": f"Bearer {await self.get_token()}"}
                async with session.get(f"{url}/auth_ping", headers=headers) as response:
                    response.raise_for_status()
                    logger.info("ping successful")
                    return Ok("Ping successful")
        except Exception as e:
            err_msg = f"Authorization failed: {e}"
            logger.error(err_msg)
            return Err(err_msg)

    @property
    def node_id(self) -> str:
        return self._node_id

    @node_id.setter
    def node_id(self, value: str) -> None:
        self._node_id = value

    @property
    def api_config(self) -> Configuration:
        return Configuration(
            host=settings.backend_api_url,
            access_token=self.token_repo.get_access_token(),
        )

    async def cycle_certificate(self) -> Result[str, str]:
        logger.info("cycling certificate ...")

        # prep directories
        private_key_path = pathlib.Path(settings.private_key_file)
        private_key_path.parent.mkdir(parents=True, exist_ok=True)
        certificate_path = pathlib.Path(settings.certificate_file)
        certificate_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("directories created")

        # generate private key and certificate
        private_key = generate_private_key()
        save_private_key_to_pem(private_key, private_key_path.as_posix())
        logger.info("private key generated")

        # generate csr and self sign certificate
        csr = generate_certificate_signing_request(private_key, self.node_id)
        logger.info("csr generated")
        certificate = self_sign_certificate(csr, private_key)
        logger.info("certificate signed")
        save_certificate_to_pem(certificate, certificate_path.as_posix())
        logger.info("certificate saved")

        # publish certificate to backend
        result = await publish_certificate_to_backend(
            certificate, self.node_id, await self.get_token()
        )
        if result.is_err():
            return result
        logger.info("certificate published")

        return Ok("Certificate cycled successfully")


def build_refresh_token_request(node_id: int, refresh_token: str) -> TokenRequest:
    return TokenRequest(
        grant_type="refresh_token",
        token_description=f"node-refresh-token-{node_id}-{datetime.datetime.now()}",
        request_type="node",
        refresh_token=refresh_token,
        node_id=node_id,
    )


def generate_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def save_private_key_to_pem(private_key: rsa.RSAPrivateKey, file_path: str) -> None:
    with open(file_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


def generate_certificate_signing_request(
    private_key: rsa.RSAPrivateKey, node_id: int
) -> x509.CertificateSigningRequest:
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Colorado"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Denver"),
                    x509.NameAttribute(
                        NameOID.ORGANIZATION_NAME, "Ambient Labs Computing"
                    ),
                    x509.NameAttribute(NameOID.COMMON_NAME, f"node-{node_id}"),
                ]
            )
        )
        .sign(private_key, hashes.SHA256())
    )
    return csr


def self_sign_certificate(
    csr: x509.CertificateSigningRequest, private_key: rsa.RSAPrivateKey
) -> x509.Certificate:
    certificate = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(csr.subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key, hashes.SHA256())
    )
    return certificate


def save_certificate_to_pem(certificate: x509.Certificate, file_path: str) -> None:
    with open(file_path, "wb") as f:
        f.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))


async def publish_certificate_to_backend(
    certificate: x509.Certificate, node_id: int, token: str
) -> Result[str, str]:
    logger.info("publishing certificate to backend ...")
    # use patch to update the node's certificate field with text of certificate
    resp_text: Optional[str] = None
    logger.debug("token: {}", token)
    try:
        async with aiohttp.ClientSession() as session:
            url = settings.backend_api_url
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            data = {
                "certificate": certificate.public_bytes(
                    encoding=serialization.Encoding.PEM
                ).decode(),
            }
            async with session.patch(
                f"{url}/nodes/{node_id}", headers=headers, json=data
            ) as response:
                resp_text = await response.text()
                response.raise_for_status()
                return Ok("Certificate published to backend")
    except Exception as e:
        err_msg = "Failed to publish certificate to backend"
        if resp_text:
            err_msg += f": {resp_text}"
        else:
            err_msg += f": {e}"
        logger.error(err_msg)
        return Err(err_msg)
