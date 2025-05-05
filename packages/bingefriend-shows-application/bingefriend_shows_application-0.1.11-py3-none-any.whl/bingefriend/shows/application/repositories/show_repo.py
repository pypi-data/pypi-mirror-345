"""Repository for managing shows."""
import logging
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.show import Show


# noinspection PyMethodMayBeStatic
class ShowRepository:
    """Repository for managing shows."""

    def get_show_by_maze_id(self, maze_id: int, db: Session) -> Show | None:
        """Get a show by its TV Maze ID.

        Args:
            maze_id (int): The ID of the show in TV Maze.
            db (Session): The database session to use.

        Returns:
            Show | None: The show object if found, else None.

        """
        show: Show | None = None

        try:
            query = db.query(Show).filter(Show.maze_id == maze_id)
            show = query.first()
        except Exception as e:
            logging.error(f"Error fetching show by maze_id {maze_id}: {e}")
            show = None
        finally:
            return show

    def create_show(self, show_data: dict[str, Any], db: Session) -> Show | None:
        """Create a new show entry in the database.

        Args:
            show_data (dict): Data of the show to be created.
            db (Session): The database session to use.

        Returns:
            Show | None: The created show object if successful, else None.

        """
        show: Show | None = None

        try:
            schedule_data = show_data.get('schedule') or {}
            image_data = show_data.get('image') or {}
            externals_data = show_data.get('externals') or {}

            show = Show(
                maze_id=show_data.get('id'),
                name=show_data.get('name'),
                type=show_data.get('type'),
                language=show_data.get('language'),
                status=show_data.get('status'),
                runtime=show_data.get('runtime'),
                averageRuntime=show_data.get('averageRuntime'),
                premiered=show_data.get('premiered'),
                ended=show_data.get('ended'),
                schedule_time=schedule_data.get('time'),
                schedule_days=",".join(schedule_data.get('days')),
                network_id=show_data.get('network_id'),
                webChannel_id=show_data.get('webChannel_id'),
                externals_imdb=externals_data.get('imdb'),
                image_medium=image_data.get('medium'),
                image_original=image_data.get('original'),
                summary=show_data.get('summary'),
                updated=show_data.get('updated')
            )
            db.add(show)
            db.flush()
            logging.info(f"Show created with ID {show.id}")
        except IntegrityError as e:
            try:
                logging.warning(f"Re-fetching show maze_id {show_data.get('id')} due to IntegrityError: {e}")
                show = self.get_show_by_maze_id(show_data.get('id'), db)
            except SQLAlchemyError as e:
                logging.error(f"Error fetching show maze_id {show_data.get('id')} after IntegrityError: {e}")
                show = None
        except SQLAlchemyError as e:
            logging.error(f"Error creating show maze_id {show_data.get('id')}: {e}")
            show = None
        except Exception as e:
            logging.error(f"Error creating show maze_id {show_data.get('id')}: {e}")
            show = None
        finally:
            return show
