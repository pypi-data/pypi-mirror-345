import ast
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from ambient_backend_api_client.models.node import Node
from sqlalchemy import delete, select

from ambient_client_common.utils import logger
from ambient_edge_server.models.sql_models import SQLNode
from ambient_edge_server.repos.sql_base_repo import SQLBaseRepository


class NodeRepo(ABC):
    @abstractmethod
    async def save_node_data(self, node: Node) -> None:
        """Save the node data to the repository.

        Args:
            node (Node): Node data
        """

    @abstractmethod
    async def get_node_data(self) -> Union[Node, None]:
        """Get the node data from the repository.

        Returns:
            Node: Node data or None if not found
            strict (bool): If True, raise an exception if the node data is not found
        """

    @abstractmethod
    async def get_node_id(self) -> int:
        """Get the node ID.

        Returns:
            int: Node ID
        """

    @abstractmethod
    async def clear_node_data(self) -> None:
        """Clear the node data from the repository."""


class SQLNodeRepo(NodeRepo, SQLBaseRepository):
    async def save_node_data(self, node: Node) -> None:
        """Save the node data to the repository.

        Args:
            node (Node): Node data
        """
        async with self.get_session() as session:
            logger.debug("Saving node data to SQL database ...")
            existing_node = (await session.scalars(select(SQLNode))).one_or_none()
            if existing_node:
                logger.debug("Node data already exists, updating ...")
                existing_node.name = node.name
                existing_node.resource_type = node.resource_type.value
                existing_node.description = node.description
                existing_node.org_id = node.org_id
                existing_node.user_id = node.user_id
                existing_node.role = node.role.value
                existing_node.live = node.live
                existing_node.architecture = node.architecture.value
                existing_node.interfaces = str(
                    list(interface.model_dump_json() for interface in node.interfaces)
                )
                existing_node.tags = str(node.tags)
                existing_node.last_seen = node.last_seen
                existing_node.error = node.error
                existing_node.status = node.status.value
                existing_node.cluster_id = node.cluster_id
                if node.docker_swarm_info:
                    existing_node.docker_swarm_info = (
                        node.docker_swarm_info.model_dump_json()
                    )
                else:
                    existing_node.docker_swarm_info = None
                await session.commit()
                await session.refresh(existing_node)
                logger.debug("Node data updated in SQL database")
                return
            sql_node = SQLNode(
                id=node.id,
                name=node.name,
                resource_type=node.resource_type.value,
                description=node.description,
                org_id=node.org_id,
                user_id=node.user_id,
                role=node.role.value,
                live=node.live,
                architecture=node.architecture.value,
                interfaces=str(
                    list(interface.model_dump_json() for interface in node.interfaces)
                ),
                tags=str(node.tags),
                last_seen=node.last_seen,
                error=node.error,
                status=node.status.value,
                cluster_id=node.cluster_id,
                docker_swarm_info=(
                    node.docker_swarm_info.model_dump_json()
                    if node.docker_swarm_info
                    else None
                ),
            )
            session.add(sql_node)
            await session.commit()
            await session.refresh(sql_node)
            logger.debug("Node data saved to SQL database")
            logger.debug("Node data: {}", sql_node.__dict__)

    async def get_node_data(self) -> Union[Node, None]:
        """Get the node data from the repository.

        Returns:
            Node: Node data or None if not found
            strict (bool): If True, raise an exception if the node data is not found
        """
        async with self.get_session() as session:
            sql_node = (await session.scalars(select(SQLNode))).one_or_none()
            if not sql_node:
                logger.info("No node data found in SQL database")
                return None
            logger.debug("Node data found in SQL database")
            logger.debug("database data: {}", sql_node.__dict__)
            node = Node(
                id=sql_node.id,
                name=sql_node.name,
                resource_type=sql_node.resource_type,
                description=sql_node.description,
                org_id=sql_node.org_id,
                user_id=sql_node.user_id,
                role=sql_node.role,
                live=sql_node.live,
                architecture=sql_node.architecture,
                interfaces=parse_sqlite_interfaces(sql_node.interfaces),
                tags=parse_sqllite_tags(sql_node.tags),
                last_seen=sql_node.last_seen,
                error=sql_node.error,
                status=sql_node.status,
                cluster_id=sql_node.cluster_id,
                docker_swarm_info=parse_sqllite_docker_swarm_info(
                    sql_node.docker_swarm_info
                ),
            )
            logger.debug("Node data: {}", node.model_dump_json(indent=4))
            logger.debug("Node record retrieved and validated.")
            return node

    async def get_node_id(self) -> Union[int, None]:
        async with self.get_session() as session:
            return (await session.scalars(select(SQLNode.id))).one_or_none()

    async def clear_node_data(self) -> None:
        """Clear the node data from the repository."""
        async with self.get_session() as session:
            await session.execute(delete(SQLNode))
            await session.commit()


def parse_sqllite_docker_swarm_info(docker_swarm_info: Union[str, None]) -> dict:
    """Parse the docker swarm info string from the SQL database into a dictionary.

    Args:
        docker_swarm_info (str | None): The docker swarm
            info string from the SQL database.

    Returns:
        dict: A dictionary representing the docker swarm info.
    """
    try:
        if not docker_swarm_info:
            return {}
        return json.loads(docker_swarm_info)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse docker swarm info string: {docker_swarm_info}")
        logger.error(f"Error: {e}")
        return {}


def parse_sqllite_tags(tags: Union[str, None]) -> List[str]:
    """Parse the tags string from the SQL database into a list of strings.

    Args:
        tags (str | None): The tags string from the SQL database.

    Returns:
        List[str]: A list of tags.
    """
    try:
        if not tags:
            return []
        return [tag.strip() for tag in tags.split(",")]
    except Exception as e:
        logger.error(f"Failed to parse tags string: {tags}")
        logger.error(f"Error: {e}")
        return []


def parse_sqlite_interfaces(interfaces: Union[str, None]) -> List[dict]:
    """Parse the interfaces string from the SQL database into a list of dictionaries."""
    try:
        if not interfaces:
            return []
        # logger.debug("type of interfaces: {}", type(interfaces))
        # logger.debug("interfaces: {}", interfaces)

        # Step 1: Safely parse the stringified Python list
        list_of_json_strings = ast.literal_eval(interfaces)
        # logger.debug("list_of_json_strings: {}", list_of_json_strings)

        # Step 2: Parse each string to a dict
        interfaces_list = [json.loads(item) for item in list_of_json_strings]
        # logger.debug("interfaces_list: {}", interfaces_list)

        return interfaces_list

    except (json.JSONDecodeError, SyntaxError, ValueError) as e:
        logger.error(f"Failed to parse interfaces string: {interfaces}")
        logger.error(f"Error: {e}")
        return []


class FileNodeRepo(NodeRepo):
    def __init__(self):
        self.home_path = Path.home() / ".ambient"
        self.node_data_path = self.home_path / ".node_data.json"

        self._init_files()

    def _init_files(self):
        if not self.node_data_path.exists():
            self._write_to_file(self.node_data_path, b"")

    def _write_to_file(self, file_path: Path, data: bytes):
        with open(file_path, "wb") as f:
            f.write(data)

    def save_node_data(self, node: Node) -> None:
        self._write_to_file(
            self.node_data_path, node.model_dump_json(indent=4).encode()
        )

    def get_node_id(self) -> Union[int, None]:
        logger.debug("Reading node ID from file: {}", self.node_data_path)
        node_data = self.get_node_data()
        if node_data:
            logger.debug("Node ID: {}", node_data.id)
            return node_data.id
        return os.getenv("AMBIENT_NODE_ID", None)

    def get_node_data(self, strict: bool = False) -> Union[Node, None]:
        logger.debug("Reading node data from file: {}", self.node_data_path)
        with open(self.node_data_path, "rb") as f:
            contents = f.read().decode()
            logger.debug("Node data: {}", contents)
            if strict:
                return Node.model_validate_json(contents)
            if not contents or contents == "":
                logger.info("No node data found")
                return None
            return Node.model_validate_json(contents)

    def clear_node_data(self) -> None:
        self._write_to_file(self.node_data_path, b"")
