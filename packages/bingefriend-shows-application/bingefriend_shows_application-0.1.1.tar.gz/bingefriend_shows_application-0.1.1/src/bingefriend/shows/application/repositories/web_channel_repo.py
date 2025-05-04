"""Repository for web channel data."""

import logging
from bingefriend.shows.core.models.web_channel import WebChannel
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError


# noinspection PyMethodMayBeStatic
class WebChannelRepository:
    """Repository to interact with web channel."""

    def get_web_channel_pk_by_maze_id(self, maze_id: int, db: Session) -> int | None:
        """Get a web channel's primary key by its TV Maze ID.

        Args:
            maze_id (int): The ID of the web channel in TV Maze.
            db (Session): The database session.

        Returns:
            int | None: The primary key of the web channel if it exists, else None.
        """
        if not maze_id:
            logging.warning("Attempted to get web channel PK with missing maze_id.")
            return None
        try:
            # Query for the primary key directly for efficiency
            web_channel_pk = db.query(WebChannel.id).filter(WebChannel.maze_id == maze_id).scalar()
            return web_channel_pk
        except SQLAlchemyError as e:
            logging.error(f"Error fetching web channel PK by maze_id {maze_id}: {e}")
            return None
        except Exception as e:  # Catch broader exceptions if necessary
            logging.error(f"Unexpected error fetching web channel PK by maze_id {maze_id}: {e}")
            return None

    def create_web_channel_if_not_exists(self, web_channel_data: dict, db: Session) -> bool:
        """Attempt to create a new web channel using INSERT IGNORE.

        Args:
            web_channel_data (dict): Data of the web channel to be created, must include 'id' (maze_id).
            db (Session): The database session.

        Returns:
            bool: True if the operation succeeded (insert attempted), False otherwise.
                  Note: This doesn't guarantee a new row was inserted.
        """
        web_channel_maze_id = web_channel_data.get('id')
        if not web_channel_maze_id:
            logging.warning("Attempted to create web channel with missing 'id' (maze_id) in data.")
            return False

        logging.debug(f"Attempting INSERT IGNORE for web channel maze_id: {web_channel_maze_id}")
        try:
            country_data = web_channel_data.get('country') or {}
            insert_stmt = mysql_insert(WebChannel).values(
                maze_id=web_channel_maze_id,
                name=web_channel_data.get('name'),
                country_name=country_data.get('name'),
                country_timezone=country_data.get('timezone'),
                country_code=country_data.get('code'),
                official_site=web_channel_data.get('officialSite')
            ).prefix_with('IGNORE')  # Add the IGNORE prefix for MySQL

            db.execute(insert_stmt)
            logging.debug(f"Executed INSERT IGNORE for web channel maze_id: {web_channel_maze_id}")
            return True  # Indicate the operation was attempted

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError during INSERT IGNORE for web channel maze_id {web_channel_maze_id}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during INSERT IGNORE for web channel maze_id {web_channel_maze_id}: {e}")
            return False
