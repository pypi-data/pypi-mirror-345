"""Service to interact with the web channel."""

import logging
from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.web_channel_repo import WebChannelRepository


# noinspection PyMethodMayBeStatic
class WebChannelService:
    """Service to manage web channel-related operations."""

    def get_or_create_web_channel(self, web_channel_data: dict | None, db: Session) -> int | None:
        """Get or create a web channel entry using an atomic approach.

        Attempts to fetch the web channel by maze_id. If not found, attempts
        an INSERT IGNORE and then fetches the ID again.

        Args:
            web_channel_data (dict | None): Data of the web channel including 'id' (maze_id).
            db (Session): The database session.

        Returns:
            int | None: The primary key (internal DB ID) of the web channel, or None if data is
            invalid or an error occurs.
        """
        if not web_channel_data:
            logging.debug("No web channel data provided to get_or_create_web_channel.")
            return None

        web_channel_maze_id = web_channel_data.get('id')
        if not web_channel_maze_id:
            logging.warning("Web channel data provided but missing 'id' (maze_id).")
            return None

        web_channel_repo = WebChannelRepository()

        # 1. First attempt to get the web channel PK
        web_channel_pk = web_channel_repo.get_web_channel_pk_by_maze_id(web_channel_maze_id, db)
        if web_channel_pk:
            logging.debug(f"Found existing web channel PK {web_channel_pk} for maze_id {web_channel_maze_id}.")
            return web_channel_pk

        # 2. If not found, attempt to create using INSERT IGNORE
        logging.debug(f"Web channel maze_id {web_channel_maze_id} not found. Attempting create.")
        created_attempted = web_channel_repo.create_web_channel_if_not_exists(web_channel_data, db)

        if not created_attempted:
            # Logged within create_web_channel_if_not_exists
            logging.error(f"Failed to execute INSERT IGNORE for web channel maze_id {web_channel_maze_id}.")
            return None  # Indicate failure

        # 3. Regardless of whether the INSERT IGNORE added a row or was ignored,
        #    the web channel *should* exist now. Fetch its PK again.
        web_channel_pk = web_channel_repo.get_web_channel_pk_by_maze_id(web_channel_maze_id, db)

        if web_channel_pk:
            logging.debug(
                f"Retrieved web channel PK {web_channel_pk} for maze_id {web_channel_maze_id} after create attempt."
            )
            return web_channel_pk
        else:
            # This case should ideally not happen if create_web_channel_if_not_exists succeeded
            logging.error(
                f"Failed to retrieve web channel PK for maze_id {web_channel_maze_id} even after INSERT IGNORE attempt."
            )
            return None
