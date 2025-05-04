"""Repository for managing episodes in the database."""

import logging
from typing import Any, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from bingefriend.shows.core.models.episode import Episode


# noinspection PyMethodMayBeStatic
class EpisodeRepository:
    """Repository for managing episodes in the database."""

    def upsert_episode(self, episode_data: Dict[str, Any], db: Session) -> Optional[int]:
        """Creates a new episode or updates an existing one based on maze_id and show_id.

        Args:
            episode_data (Dict[str, Any]): A dictionary containing episode data from the API.
                                           It's expected that 'show_id' and 'season_id'
                                           (internal DB IDs) have been added to this dict
                                           by the calling service.
            db (Session): The database session to use for database operations.

        Returns:
            Optional[int]: The internal database ID of the created/updated episode,
                           or None if an error occurred or identifiers were missing.
        """
        maze_id = episode_data.get("id")
        show_id = episode_data.get("show_id")

        episode_id = None

        if not maze_id:
            logging.error("Cannot upsert episode: 'id' (maze_id) is missing from episode_data.")
            return None
        if not show_id:
            logging.error(f"Cannot upsert episode maze_id {maze_id}: 'show_id' is missing from episode_data.")
            return None

        season_id = episode_data.get("season_id")

        try:
            existing_episode = db.query(Episode).filter(
                Episode.maze_id == maze_id,
                Episode.show_id == show_id
            ).first()

            airdate = episode_data.get('airdate')
            airstamp = episode_data.get('airstamp')
            db_airdate = airdate if airdate else None
            db_airstamp = airstamp if airstamp else None
            image_data = episode_data.get("image") or {}

            episode_attrs = {
                "maze_id": maze_id,
                "url": episode_data.get("url"),
                "name": episode_data.get("name"),
                "number": episode_data.get("number"),
                "type": episode_data.get("type"),
                "airdate": db_airdate,
                "airtime": episode_data.get("airtime"),
                "airstamp": db_airstamp,
                "runtime": episode_data.get("runtime"),
                "image_medium": image_data.get("medium"),
                "image_original": image_data.get("original"),
                "summary": episode_data.get("summary"),
                "show_id": show_id,
                "season_id": season_id,
            }

            if existing_episode:
                logging.debug(
                    f"Updating existing episode with maze_id: {maze_id} for show_id: {show_id} (DB ID: "
                    f"{existing_episode.id})"
                )

                update_data = episode_attrs

                for key, value in update_data.items():
                    setattr(existing_episode, key, value)

                episode_id = existing_episode.id

                logging.debug(f"Successfully updated episode maze_id: {maze_id}, internal DB ID: {episode_id}")

            else:
                logging.debug(f"Creating new episode with maze_id: {maze_id} for show_id: {show_id}")

                new_episode = Episode(**episode_attrs)

                db.add(new_episode)
                db.flush()

                episode_id = new_episode.id

                logging.debug(f"Successfully created episode maze_id: {maze_id}, internal DB ID: {episode_id}")

            return episode_id

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError upserting episode entry for maze_id {maze_id}, show_id {show_id}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error upserting episode entry for maze_id {maze_id}, show_id {show_id}: {e}",
                          exc_info=True)
            return None
        finally:
            return episode_id
