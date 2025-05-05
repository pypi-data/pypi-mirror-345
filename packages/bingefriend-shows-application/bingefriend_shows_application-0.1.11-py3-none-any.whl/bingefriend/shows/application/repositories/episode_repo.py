"""Repository for managing episodes in the database."""
import logging
from typing import Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.episode import Episode


# noinspection PyMethodMayBeStatic
class EpisodeRepository:
    """Repository for managing episodes in the database."""

    def create_episode(self, episode_data: dict[str, Any], db: Session) -> Episode | None:
        """Add a new episode to the database.

        Args:
            episode_data (dict): A dictionary containing episode data.
            db (Session): The database session to use.

        Returns:
            Episode | None: The created episode object if successful, else None.

        """
        episode: Episode | None = None

        image_data = episode_data.get("image") or {}

        try:
            episode = Episode(
                maze_id=episode_data.get("id"),
                name=episode_data.get("name"),
                number=episode_data.get("number"),
                type=episode_data.get("type"),
                airdate=episode_data.get("airdate"),
                airtime=episode_data.get("airtime"),
                airstamp=episode_data.get("airstamp"),
                runtime=episode_data.get("runtime"),
                image_medium=image_data.get("medium"),
                image_original=image_data.get("original"),
                summary=episode_data.get("summary"),
                season_id=episode_data.get("season_id"),
                show_id=episode_data.get("show_id")
            )
            db.add(episode)
            db.flush()
            logging.info(f"Episode created with ID {episode.id}")
        except IntegrityError as e:
            logging.warning(f"Episode maze_id {episode_data.get('id')} already exists: {e}")
            episode = None
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error creating episode maze_id {episode_data.get('id')}: {e}")
            episode = None
        except Exception as e:
            logging.error(f"Error creating episode maze_id {episode_data.get('id')}: {e}")
            episode = None
        finally:
            return episode
