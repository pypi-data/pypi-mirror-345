"""Service for episode-related operations."""

import logging
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from bingefriend.shows.core.models import Episode, Season
from bingefriend.shows.client_tvmaze.tvmaze_api import TVMazeAPI
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
        show_episodes: list[dict[str, Any]] | None = None

        try:
            tvmaze_api = TVMazeAPI()

            show_episodes = tvmaze_api.get_episodes(show_id)

            if show_episodes is None:
                logging.info(f"API returned None (404 likely) for show ID {show_id}. Stopping pagination.")
                show_episodes = None

            if not show_episodes:
                logging.info(f"No episodes found for show ID {show_id}. Ending pagination.")
                show_episodes = None

            if show_episodes:
                logging.info(f"Retrieved {len(show_episodes)} episodes for show ID {show_id}.")
        except Exception as e:
            logging.exception(f"Error retrieving episode index page for show ID {show_id}: {e}")
            show_episodes = None
        finally:
            return show_episodes

    def process_episode_record(self, episode_data: dict, show_id: int, db: Session) -> Episode | None:
        """Process a single episode record and store it in the database.

        Args:
            episode_data (dict): The episode record to process.
            show_id (int): The ID of the show to associate with the episode.
            db (Session): The database session to use.

        Returns:
            Episode | None: The processed episode object or None if not created.

        """

        episode_data["show_id"] = show_id

        # Clean up the record by removing empty strings
        for key in ['airdate', 'airtime', 'airstamp']:
            if episode_data.get(key) == '':
                episode_data[key] = None

        # Convert airstamp to datetime
        airstamp_str = episode_data.get('airstamp')
        parsed_airstamp = None
        if airstamp_str:
            try:
                # Parse the ISO 8601 string into a timezone-aware datetime object
                parsed_airstamp = datetime.fromisoformat(airstamp_str)
            except (ValueError, TypeError) as e:
                logging.warning(f"Could not parse airstamp '{airstamp_str}': {e}")
                # Handle error appropriately

        # Update the data before passing to SQLAlchemy
        episode_data['airstamp'] = parsed_airstamp

        # Get season ID for the episode
        season_service = SeasonService()
        season_number: int = episode_data.get("season")
        season: Season | None = season_service.get_season_by_show_id_and_season_number(show_id, season_number, db)
        episode_data["season_id"] = season.id if season else None

        episode_repo = EpisodeRepository()
        episode = episode_repo.create_episode(episode_data, db)

        return episode
