"""Service to manage network-related operations."""

from typing import Any
from sqlalchemy.orm import Session
from bingefriend.shows.application import WebChannelService
from bingefriend.shows.application.repositories.season_repo import SeasonRepository
from bingefriend.shows.application.services.network_service import NetworkService
from bingefriend.shows.core.models import Network, WebChannel, Season
from bingefriend.tvmaze_client.tvmaze_api import TVMazeAPI


# noinspection PyMethodMayBeStatic
class SeasonService:
    """Service to handle season-related operations."""

    def fetch_season_index_page(self, show_id: int) -> list[dict[str, Any]] | None:
        """Fetch a page of seasons for a given show_id from the external API.

        Args:
            show_id (int): The ID of the show to fetch seasons for.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing season data.

        """

        tvmaze_api: TVMazeAPI = TVMazeAPI()

        seasons: list[dict[str, Any]] | None = tvmaze_api.get_seasons(show_id)

        return seasons

    def process_season_record(self, record: dict, show_id: int, db: Session) -> Season | None:
        """Process a single season record and return the processed data.

        Args:
            record (dict): The season record to process.
            show_id (int): The ID of the show to associate with the season.
            db (Session): The database session to use.

        """

        record["show_id"]: int = show_id

        # Get network data from the record
        if record.get("network"):
            network_service: NetworkService = NetworkService()
            network_data: dict = record["network"]
            network: Network | None = network_service.get_or_create_network(network_data, db)
            record["network_id"]: int = network.id if network else None

        # Get web channel data from the record
        if record.get("web_channel"):
            web_channel_service: WebChannelService = WebChannelService()
            web_channel_data: dict = record["web_channel"]
            web_channel: WebChannel | None = web_channel_service.get_or_create_web_channel(web_channel_data, db)
            record["web_channel_id"]: int = web_channel.id if web_channel else None

        # Process the season record
        season_repo: SeasonRepository = SeasonRepository()
        season_data: dict = record
        season: dict | None = season_repo.create_season(season_data, db)

        return season

    def get_season_by_show_id_and_number(self, show_id: int, season_number: int, db: Session) -> Season | None:
        """Get the season ID for a given show ID and season number.

        Args:
            show_id (int): The ID of the show.
            season_number (int): The season number.
            db (Session): The database session to use.

        Returns:
            Season | None: The season object if found, otherwise None.

        """
        season_repo = SeasonRepository()

        season: Season | None = season_repo.get_season_by_show_id_and_number(show_id, season_number, db)

        return season
