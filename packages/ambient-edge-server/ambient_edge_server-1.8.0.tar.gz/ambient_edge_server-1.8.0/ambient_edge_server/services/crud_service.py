from ambient_backend_api_client import NodeOutput as Node

from ambient_client_common.repositories import backend_api_repo
from ambient_client_common.utils import logger
from ambient_edge_server.repos.node_repo import NodeRepo
from ambient_edge_server.services.authorization_service import AuthorizationService


class CRUDService:
    """A service for interacting with stateful data on the node"""

    def __init__(self, node_repo: NodeRepo, auth_svc: AuthorizationService) -> None:
        self.node_repo = node_repo
        self.auth_svc = auth_svc

    async def get_node_data(self) -> Node:
        """Get the node data from the repository.

        Returns:
            Node: Node data
        """
        logger.info("Fetching Node data from repository ...")
        return await self.node_repo.get_node_data()

    async def clear_node_data(self) -> None:
        """Clear the node data in the repository.

        Returns:
            None
        """
        logger.info("Clearing Node data from repository ...")
        await self.node_repo.clear_node_data()
        logger.info("Node data cleared")

    async def refresh_node_data(self) -> Node:
        """Fetch Node data from API and save to repo

        Returns:
            Node: Node data
        """

        logger.info("Updating Node data ...")
        # get node ID from repo
        node_id = await self.node_repo.get_node_id()
        logger.debug("CRUDService.update_node_data() - Node ID: {}", node_id)

        # make API call
        node = await backend_api_repo.get_node(
            node_id=node_id, headers=self.auth_svc.get_auth_headers()
        )
        logger.info("Node data fetched")

        # save data using node repo
        logger.info("Saving Node data to repository ...")
        await self.node_repo.save_node_data(node)
        logger.info("Node data saved")

        # return node data
        return node

    async def patch_node(self, **values):
        node_id = await self.node_repo.get_node_id()
        logger.debug("CRUDService.patch_node() - Node ID: {}", node_id)

        try:
            updated_node = await backend_api_repo.patch_node(
                node_id=node_id,
                headers=await self.auth_svc.get_auth_headers(),
                **values
            )
        except Exception as e:
            logger.error("Error patching node data: {}", e)
            raise e

        # save data using node repo
        logger.info("Saving Node data to repository ...")
        await self.node_repo.save_node_data(updated_node)
        logger.info("Node data saved")

        # return updated_node data
        return updated_node
