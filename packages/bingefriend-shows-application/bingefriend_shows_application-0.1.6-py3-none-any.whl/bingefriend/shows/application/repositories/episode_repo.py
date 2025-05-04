"""Repository for episode data."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from bingefriend.shows.core.models.episode import Episode


# noinspection PyMethodMayBeStatic
class EpisodeRepository:
    """Repository for episode data."""

    def upsert_episode(self, episode_data: dict, show_id: int, season_id: int, db: Session) -> int | None:
        """Create a new episode entry or update an existing one based on maze_id.

        Args:
            episode_data (dict): Data of the episode to be created or updated. Must include 'id' (maze_id).
            show_id (int): The internal DB ID of the show this episode belongs to.
            season_id (int): The internal DB ID of the season this episode belongs to.
            db (Session): The database session.

        Returns:
            int | None: The primary key (internal DB ID) of the created/updated episode, or None on error.
        """
        maze_id = episode_data.get("id")
        # noinspection PyUnusedLocal
        episode_id = None  # Initialize episode_id

        if not maze_id:
            logging.error(
                f"Cannot upsert episode for show_id {show_id}, season_id {season_id}: 'id' (maze_id) is missing.")
            return None
        if not show_id:
            logging.error(f"Cannot upsert episode for maze_id {maze_id}: show_id is missing.")
            return None
        if not season_id:
            logging.error(f"Cannot upsert episode for maze_id {maze_id}: season_id is missing.")
            return None

        try:
            # Look for existing episode by maze_id AND show_id
            existing_episode = db.query(Episode).filter(
                Episode.maze_id == maze_id,
                Episode.show_id == show_id
                # Assuming maze_id is unique per show. If unique per season, add: Episode.season_id == season_id
            ).first()

            airdate = episode_data.get('airdate')
            airstamp = episode_data.get('airstamp')
            db_airdate = airdate if airdate else None
            db_airstamp = airstamp if airstamp else None
            image_data = episode_data.get("image") or {}

            episode_attrs = {
                "show_id": show_id,
                "season_id": season_id,
                "maze_id": maze_id,
                "url": episode_data.get("url"),
                "name": episode_data.get("name"),
                "seasonNumber": episode_data.get("season"),  # API uses 'season', model uses 'seasonNumber'
                "number": episode_data.get("number"),
                "type": episode_data.get("type"),
                "airdate": db_airdate,
                "airstamp": db_airstamp,
                "runtime": episode_data.get("runtime"),
                "image_medium": image_data.get("medium"),
                "image_original": image_data.get("original"),
                "summary": episode_data.get("summary"),
            }

            if existing_episode:
                logging.debug(
                    f"Updating existing episode maze_id: {maze_id} for show_id: {show_id} (DB ID: "
                    f"{existing_episode.id})"
                )
                for key, value in episode_attrs.items():
                    setattr(existing_episode, key, value)
                episode_id = existing_episode.id
                logging.info(
                    f"Successfully prepared update for episode maze_id: {maze_id}, internal DB ID: {episode_id}")

            else:
                logging.debug(f"Creating new episode maze_id: {maze_id} for show_id: {show_id}, season_id: {season_id}")
                new_episode = Episode(**episode_attrs)
                db.add(new_episode)
                db.flush()  # <--- Add flush here
                episode_id = new_episode.id  # Read ID after flush
                if episode_id:
                    logging.info(f"Successfully created episode maze_id: {maze_id}, internal DB ID: {episode_id}")
                else:
                    logging.error(f"Failed to retrieve generated ID for new episode maze_id: {maze_id} after flush.")
                    # db.rollback()
                    return None  # Return None if ID retrieval failed

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError upserting episode maze_id {maze_id} for show_id {show_id}: {e}")
            # db.rollback()
            return None
        except Exception as e:
            logging.error(f"Unexpected error upserting episode maze_id {maze_id} for show_id {show_id}: {e}",
                          exc_info=True)
            # db.rollback()
            return None

        return episode_id
