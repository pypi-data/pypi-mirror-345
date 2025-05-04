"""Service to manage network-related operations."""
import logging
from typing import Any

from sqlalchemy.orm import Session

from bingefriend.shows.application.repositories.season_repo import SeasonRepository
from bingefriend.shows.application.services.network_service import NetworkService
from bingefriend.tvmaze_client.tvmaze_api import TVMazeAPI


# noinspection PyMethodMayBeStatic
class SeasonService:
    """Service to handle season-related operations."""

    def fetch_season_index_page(self, show_id: int) -> list[dict[str, Any]]:
        """Fetch a page of seasons for a given show_id from the external API.

        Args:
            show_id (int): The ID of the show to fetch seasons for.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing season data.

        """

        tvmaze_api: TVMazeAPI = TVMazeAPI()

        seasons: list[dict[str, Any]] = tvmaze_api.get_seasons(show_id)

        if not seasons:
            raise ValueError(f"No seasons found for show_id: {show_id}")

        return seasons

    def process_season_record(self, record: dict[str, Any], show_id: int, db: Session) -> None:
        """Process a single season record, creating or updating it.

        Args:
            record (dict[str, Any]): The season record data from the API.
            show_id (int): The internal database ID of the show to associate with the season.
            db (Session): The database session to use for database operations.

        """
        season_maze_id = record.get('id')

        if not season_maze_id:
            logging.error(f"Season record for show_id {show_id} is missing 'id' (maze_id). Skipping processing.")

            return

        logging.debug(f"Processing season record for show_id: {show_id}, season maze_id: {season_maze_id}")

        record["show_id"] = show_id

        network_service = NetworkService()
        network_info = record.get("network")
        record["network_id"] = network_service.get_or_create_network(network_info, db) if network_info else None

        season_repo = SeasonRepository()
        season_db_id = season_repo.upsert_season(record, db)

        if season_db_id:
            logging.info(
                f"Successfully upserted season maze_id: {season_maze_id} for show_id: {show_id} (DB ID: {season_db_id})"
            )
            return

        logging.error(f"Failed to upsert season maze_id: {season_maze_id} for show_id: {show_id}")

    def get_season_id_by_show_id_and_number(self, show_id: int, season_number: int, db: Session) -> int:
        """Get the season ID for a given show ID and season number.

        Args:
            show_id (int): The ID of the show.
            season_number (int): The season number.
            db (Session): The database session to use for database operations.

        Returns:
            int: The ID of the season.

        """

        season_repo = SeasonRepository()

        season_id: int = season_repo.get_season_id_by_show_id_and_number(show_id, season_number, db)

        return season_id
