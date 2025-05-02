from ambient_backend_api_client import NodeOutput as Node
from fastapi import APIRouter, Depends, HTTPException

from ambient_client_common.models.docker_models import DockerRoleEnum
from ambient_client_common.utils import logger
from ambient_edge_server.services import crud_service, docker_service, service_manager

router = APIRouter(prefix="/data", tags=["data", "nodes"])


# GET node data
@router.get("/node", response_model=Node)
async def get_node_data(
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
    username: str = Depends(
        service_manager.svc_manager._authorization_service.authenticate
    ),
):
    node_data = await crud_service.get_node_data()
    if not node_data:
        raise HTTPException(status_code=404, detail="Node data not found")
    return node_data


# Refresh node data
@router.post("/node/refresh", response_model=Node)
async def update_node_data(
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
):
    node_data = await crud_service.refresh_node_data()
    return node_data


# PATCH node data
@router.patch("/node")
async def patch_node_data(
    data: dict,
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
    _: str = Depends(service_manager.svc_manager._authorization_service.authenticate),
):
    logger.debug("PATCH node data: {}", data)
    node_data = await crud_service.patch_node(**data)
    return node_data


# DELETE node data
@router.delete("/node")
async def delete_node_data(
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
):
    await crud_service.clear_node_data()
    return {"message": "Node data deleted"}


# GET Docker swarm join token
@router.get("/swarm/join-token")
async def get_swarm_join_token(
    role: DockerRoleEnum,
    docker_svc: docker_service.DockerService = Depends(
        service_manager.svc_manager.get_docker_service
    ),
):
    join_token = docker_svc.get_join_token(role=role)
    return {"join_token": join_token}
