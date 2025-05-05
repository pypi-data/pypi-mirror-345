"""Service to interact with the web channel."""

from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.web_channel_repo import WebChannelRepository
from bingefriend.shows.core.models import WebChannel


# noinspection PyMethodMayBeStatic
class WebChannelService:
    """Service to manage web channel-related operations."""

    def get_or_create_web_channel(self, web_channel_data: dict, db: Session) -> WebChannel | None:
        """Get or create a web channel entry in the database.

        Args:
            web_channel_data (dict): Data of the web channel to be created or fetched.
            db (Session): The database session to use.

        Returns:
            WebChannel | None: The web channel object if it exists or is created, else None.

        """

        web_channel_repo: WebChannelRepository = WebChannelRepository()

        maze_id: int = web_channel_data.get('id')

        if not maze_id:
            return None

        web_channel: WebChannel | None = web_channel_repo.get_web_channel_by_maze_id(maze_id, db)

        # If web channel exists, get primary key
        if not web_channel:
            web_channel = web_channel_repo.create_web_channel(web_channel_data, db)

        return web_channel
