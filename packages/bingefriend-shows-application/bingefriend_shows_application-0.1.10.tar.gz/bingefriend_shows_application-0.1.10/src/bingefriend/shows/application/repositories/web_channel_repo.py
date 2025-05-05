"""Repository for web channel data."""

import logging
from sqlalchemy import select, Select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.web_channel import WebChannel


# noinspection PyMethodMayBeStatic
class WebChannelRepository:
    """Repository to interact with web channel."""

    def get_web_channel_by_maze_id(self, maze_id: int, db: Session) -> WebChannel | None:
        """Get a web channel by its TV Maze ID.

        Args:
            maze_id (int): The ID of the web channel in TV Maze.
            db (Session): The database session to use.

        Returns:
            WebChannel | None: The web channel object if found, else None.

        """
        web_channel: WebChannel | None = None

        try:
            query: Select = select(WebChannel).where(WebChannel.maze_id == maze_id)
            web_channel = db.execute(query).scalars().first()
        except Exception as e:
            logging.error(f"Error fetching web channel by maze_id {maze_id}: {e}")
            web_channel = None
        finally:
            return web_channel

    def create_web_channel(self, web_channel_data, db: Session) -> WebChannel | None:
        """Create a new web channel entry in the database.

        Args:
            web_channel_data (dict): Data of the web channel to be created.
            db (Session): The database session to use.

        Returns:
            WebChannel | None: The created web channel object if successful, else None.

        """
        web_channel: WebChannel | None = None

        try:
            country_data: dict = web_channel_data.get('country') or {}

            web_channel = WebChannel(
                maze_id=web_channel_data.get('id'),
                name=web_channel_data.get('name'),
                country_name=country_data.get('name'),
                country_timezone=country_data.get('timezone'),
                country_code=country_data.get('code'),
                official_site=web_channel_data.get('officialSite'),
            )
            db.add(web_channel)
            db.flush()
            logging.info(f"Web channel created with ID {web_channel.id}")
        except IntegrityError as e:
            try:
                logging.warning(
                    f"Re-fetching web channel maze_id {web_channel_data.get('id')} due to IntegrityError: {e}"
                )
                web_channel = self.get_web_channel_by_maze_id(web_channel_data.get('id'), db)
            except Exception as e:
                logging.error(
                    f"Error fetching web channel maze_id {web_channel_data.get('id')} after IntegrityError: {e}"
                )
                web_channel = None
        except SQLAlchemyError as e:
            logging.error(f"Error creating web channel maze_id {web_channel_data.get('id')}: {e}")
            web_channel = None
        except Exception as e:
            print(f"Error creating web channel maze_id {web_channel_data.get('id')}: {e}")
            web_channel = None
        finally:
            return web_channel
