"""Service to interact with the web channel."""

from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.web_channel_repo import WebChannelRepository


# noinspection PyMethodMayBeStatic
class WebChannelService:
    """Service to manage web channel-related operations."""

    def get_or_create_web_channel(self, web_channel_data, db: Session) -> int | None:
        """Get or create a web channel entry in the database.

        Args:
            web_channel_data (dict): Data of the web channel to be created or fetched.
            db (Session): The database session.

        Returns:
            int | None: The primary key of the web channel if it exists or is created, else None.

        """

        web_channel_repo = WebChannelRepository()

        maze_id = web_channel_data.get('id')

        if not maze_id:
            return None

        web_channel_pk = web_channel_repo.get_web_channel_by_maze_id(maze_id, db)

        if web_channel_pk:
            return web_channel_pk

        web_channel_pk = web_channel_repo.create_web_channel(web_channel_data, db)

        return web_channel_pk
