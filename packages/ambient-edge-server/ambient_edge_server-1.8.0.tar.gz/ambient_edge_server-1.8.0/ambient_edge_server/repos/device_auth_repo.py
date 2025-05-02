from typing import Optional

from sqlalchemy import delete, select

from ambient_client_common.utils import logger
from ambient_edge_server.models.sql_models import (
    SQLAPIUser,
    SQLDeviceAuthRequest,
    SQLToken,
)
from ambient_edge_server.repos.sql_base_repo import SQLBaseRepository


class SQLDeviceAuthRepository(SQLBaseRepository):
    """
    SQLDeviceRepository is a concrete implementation of the DeviceRepository interface.
    It uses SQLAlchemy to interact with a PostgreSQL database.
    """

    async def get_api_user(
        self, username: str = "", id: Optional[int] = None
    ) -> Optional[SQLAPIUser]:
        """
        Retrieve the API user from the database.

        Args:
            username (str): The username of the API user.
            id (int): The ID of the API user.

        Returns:
            SQLAPIUser: The API user information.
        """
        if not username and not id:
            raise ValueError("Either username or id must be provided.")
        async with self.get_session() as session:
            if id is not None:
                return (
                    await session.scalars(select(SQLAPIUser).where(SQLAPIUser.id == id))
                ).one_or_none()
            return (
                await session.scalars(
                    select(SQLAPIUser).where(SQLAPIUser.username == username)
                )
            ).one_or_none()

    async def save_api_user(self, api_user: SQLAPIUser) -> SQLAPIUser:
        """
        Save the API user to the database.

        Args:
            api_user (SQLAPIUser): The API user information to save.
        """
        async with self.get_session() as session:
            existing_user = (
                await session.scalars(
                    select(SQLAPIUser).where(SQLAPIUser.username == api_user.username)
                )
            ).one_or_none()
            if existing_user:
                existing_user.password_hash = api_user.password_hash
                await session.commit()
                await session.refresh(existing_user)
                return existing_user
            session.add(api_user)
            await session.commit()
            await session.refresh(api_user)
            return api_user

    async def delete_api_user(self, id: int) -> None:
        """
        Delete the API user from the database.

        Args:
            id (int): The ID of the API user to delete.
        """
        async with self.get_session() as session:
            await session.execute(delete(SQLAPIUser).where(SQLAPIUser.id == id))
            await session.commit()
            return

    async def get_device_auth_request(self) -> Optional[SQLDeviceAuthRequest]:
        """
        Retrieve the device authentication information from the database.

        Returns:
            SQLDeviceAuthRequest: The device authentication information.
        """
        async with self.get_session() as session:
            request = (
                await session.scalars(select(SQLDeviceAuthRequest))
            ).one_or_none()
            logger.debug(f"get_device_auth_request: {request}")
            logger.debug(f"request dir: {dir(request)}")
            return request

    async def save_device_auth_request(self, device_auth: SQLDeviceAuthRequest) -> None:
        """
        Save the device authentication information to the database.

        Args:
            device_auth (SQLDeviceAuthRequest): The device authentication
                information to save.
        """
        async with self.get_session() as session:
            session.add(device_auth)
            await session.commit()
            await session.refresh(device_auth)
            return device_auth

    async def delete_device_auth_request(self) -> None:
        """
        Delete the device authentication information from the database.
        """
        async with self.get_session() as session:
            await session.execute(delete(SQLDeviceAuthRequest))
            await session.commit()
            return

    async def get_token(self) -> Optional[SQLToken]:
        """
        Retrieve the token from the database.

        Returns:
            SQLToken: The token information.
        """
        async with self.get_session() as session:
            return (await session.scalars(select(SQLToken))).one_or_none()

    async def save_token(self, token: SQLToken) -> SQLToken:
        """
        Save the token to the database.

        Args:
            token (c): The token information to save.
        """
        async with self.get_session() as session:
            await session.execute(delete(SQLToken))

            session.add(token)
            await session.commit()
            await session.refresh(token)
            return token

    async def delete_token(self) -> None:
        """
        Delete the token from the database.
        """
        async with self.get_session() as session:
            await session.execute(delete(SQLToken))
            await session.commit()
            return
