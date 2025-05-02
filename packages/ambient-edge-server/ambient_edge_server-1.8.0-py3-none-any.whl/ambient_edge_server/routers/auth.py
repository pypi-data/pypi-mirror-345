from ambient_backend_api_client import DeviceAuthorizationRequest
from fastapi import APIRouter, Depends, HTTPException

from ambient_client_common.utils import logger
from ambient_edge_server.services.authorization_service import AuthorizationService
from ambient_edge_server.services.service_manager import svc_manager

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/")
async def authorize_node(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
):
    """Authorize a node to connect to the backend API

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    await auth_svc.authorize_node()
    return {"status": "success"}


@router.post("/request", response_model=DeviceAuthorizationRequest)
async def request_node_authorization(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
) -> DeviceAuthorizationRequest:
    """Authorize a node to connect to the backend API

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    return await auth_svc.request_device_authorization()


@router.get("/status")
async def get_auth_status(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
):
    """Get authorization status

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    result = await auth_svc.verify_authorization_status()
    if result.is_ok():
        return {"status": result.unwrap()}
    return {"status": result.unwrap_err()}


@router.post("/cycle-certificate")
async def cycle_certificate(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
):
    """Cycle the certificate

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    result = await auth_svc.cycle_certificate()
    if result.is_err():
        return {"status": result.unwrap_err()}
    return {"status": "success"}


@router.post("/refresh")
async def refresh_token(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
):
    """Refresh the token

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    result = await auth_svc.refresh_token()
    if result.is_err():
        return {"status": result.unwrap_err()}
    return {"status": "success"}


@router.get("/token")
async def get_token(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
    username: str = Depends(svc_manager.get_authorization_service().authenticate),
):
    """Get the token

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    logger.info("User {} is requesting a token", username)
    token = await auth_svc.get_token()
    if not token:
        raise HTTPException(
            status_code=401, detail="Token not found. Please authorize the node."
        )
    return {"token": token}


@router.post("/api-users")
async def neighbor_node_auth(
    auth_svc: AuthorizationService = Depends(svc_manager.get_authorization_service),
    claims: dict = Depends(
        svc_manager.get_authorization_service().authenticate_backend_token
    ),
):
    """Authorize a neighbor node to connect to the backend API

    Args:
        auth_svc (AuthorizationService, optional): Defaults to
            Depends(svc_manager.get_authorization_service).

    Returns:
        dict: Response
    """
    auth_data = await auth_svc.add_local_api_user(claims)
    return auth_data
