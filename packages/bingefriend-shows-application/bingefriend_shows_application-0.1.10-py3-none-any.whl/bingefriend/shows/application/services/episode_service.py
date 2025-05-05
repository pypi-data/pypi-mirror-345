"""Service for episode-related operations."""

from typing import Any
from sqlalchemy.orm import Session
from bingefriend.shows.core.models import Episode, Season
from bingefriend.tvmaze_client.tvmaze_api import TVMazeAPI
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
            dict: A dictionary containing the episodes data.

        """

        tvmaze_api = TVMazeAPI()

        show_episodes = tvmaze_api.get_episodes(show_id)

        if not show_episodes:
            raise ValueError(f"No episodes found for show_id: {show_id}")
        return show_episodes

    def process_episode_record(self, record: dict, show_id: int, db: Session) -> Episode | None:
        """Process a single episode record and store it in the database.

        Args:
            record (dict): The episode record to process.
            show_id (int): The ID of the show to associate with the episode.
            db (Session): The database session to use.

        Returns:
            Episode | None: The processed episode object or None if not created.

        """

        record["show_id"] = show_id

        # Get season ID for the episode
        season_service = SeasonService()
        season_number = record.get("season")
        season: Season | None = season_service.get_season_by_show_id_and_number(show_id, season_number, db)
        record["season_id"] = season.id if season else None

        episode_repo = EpisodeRepository()
        episode = episode_repo.create_episode(record, db)

        return episode
