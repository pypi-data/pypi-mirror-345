"""Service for managing episodes."""

import logging
from typing import Any, Dict
from bingefriend.tvmaze_client.tvmaze_api import TVMazeAPI
from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.episode_repo import EpisodeRepository
from bingefriend.shows.application.services.season_service import SeasonService


# noinspection PyMethodMayBeStatic
class EpisodeService:
    """Service for episode-related operations."""

    def fetch_episode_index_page(self, show_id: int) -> list[dict[str, Any]]:
        """Fetch all episodes for a given show_id from the external API.

        Args:
            show_id (int): The ID of the show to fetch episodes for.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing the episodes data.

        Raises:
            ValueError: If no episodes are found for the show_id.
        """
        tvmaze_api = TVMazeAPI()
        show_episodes = tvmaze_api.get_episodes(show_id)

        if not show_episodes:
            logging.warning(f"No episodes found via API for show_id: {show_id}")

            return []  # Return empty list

        return show_episodes

    def process_episode_record(self, record: Dict[str, Any], show_id: int, db: Session) -> None:
        """Process a single episode record, creating or updating it.

        Args:
            record (Dict[str, Any]): The episode record data from the API.
            show_id (int): The internal database ID of the show associated with the episode.
            db (Session): The database session to use for database operations.

        """
        episode_maze_id = record.get('id')
        if not episode_maze_id:
            logging.error(f"Episode record for show_id {show_id} is missing 'id' (maze_id). Skipping processing.")

            return

        logging.debug(f"Processing episode record for show_id: {show_id}, episode maze_id: {episode_maze_id}")

        record["show_id"] = show_id

        season_number = record.get("season")

        season_id = None

        if season_number is not None:
            season_service = SeasonService()

            season_id = season_service.get_season_id_by_show_id_and_number(
                show_id=show_id, season_number=season_number, db=db
            )

        else:
            logging.warning(
                f"Episode maze_id {episode_maze_id} for show_id {show_id} is missing 'season' number. Cannot link to "
                f"season."
            )

        if season_id is None and season_number is not None:
            logging.error(
                f"Could not find internal season_id for show_id {show_id}, season number {season_number}. Skipping"
                f" episode maze_id {episode_maze_id}."
            )

            return

        record['season_id'] = season_id  # Add internal season_id to record

        episode_repo = EpisodeRepository()

        episode_db_id = episode_repo.upsert_episode(record, db)

        if episode_db_id:
            logging.info(
                f"Successfully upserted episode maze_id: {episode_maze_id} for show_id: {show_id} (DB ID: "
                f"{episode_db_id})"
            )
        else:
            logging.error(f"Failed to upsert episode maze_id: {episode_maze_id} for show_id: {show_id}")
