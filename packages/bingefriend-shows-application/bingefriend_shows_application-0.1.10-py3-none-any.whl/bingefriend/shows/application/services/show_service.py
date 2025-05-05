"""Service to handle the ingestion of show data from an external API."""

import logging
from typing import Any
from sqlalchemy.orm import Session
from bingefriend.shows.application.services.episode_service import EpisodeService
from bingefriend.shows.application.services.genre_service import GenreService
from bingefriend.shows.application.services.network_service import NetworkService
from bingefriend.shows.application.services.season_service import SeasonService
from bingefriend.shows.application.services.show_genre_service import ShowGenreService
from bingefriend.shows.application.repositories.show_repo import ShowRepository
from bingefriend.shows.application.services.web_channel_service import WebChannelService
from bingefriend.shows.core.models import WebChannel, Network, Show, Genre, ShowGenre
from bingefriend.tvmaze_client.tvmaze_api import TVMazeAPI


# noinspection PyMethodMayBeStatic
class ShowService:
    """Service to handle the ingestion of show data from an external API."""

    def fetch_show_index_page(self, page_number: int) -> dict[str, Any] | None:
        """Fetch a page of shows from the external API and enqueue the next page.

        Args:
            page_number (int): The page number to fetch.

        Returns:
            dict[str, Any] | None: A dictionary containing the shows and the next page number, or None if no more pages.

        """

        try:
            tvmaze_api: TVMazeAPI = TVMazeAPI()
            shows_summary: list[dict[str, Any]] = tvmaze_api.get_shows(page=page_number)

            if shows_summary is None:
                logging.info(f"API returned None (404 likely) for page {page_number}. Stopping pagination.")
                return None

            if not shows_summary:
                logging.info(f"No shows found on page {page_number}. Ending pagination.")
                return None
        except Exception as init_err:
            logging.exception(f"Failed to get dependencies for ingestion service: {init_err}")
            raise init_err  # Cannot proceed

        return {
            'records': shows_summary,
            'next_page': page_number + 1 if shows_summary else None
        }

    def process_show_record(self, record: dict[str, Any], db: Session) -> None:
        """Process a single show record.

        Args:
            record (dict[str, Any]): The show record to process.
            db (Session): The database session to use.

        """

        # Process network data from the record
        network_service: NetworkService = NetworkService()
        network_info: dict | None = record.get('network')

        if network_info:
            network: Network | None = network_service.get_or_create_network(network_info, db)
            record['network_id']: int | None = network.id if network else None

        # Process web channel data from the record
        web_channel_service: WebChannelService = WebChannelService()
        web_channel_info: dict | None = record.get('webChannel')

        if web_channel_info:
            web_channel: WebChannel | None = web_channel_service.get_or_create_web_channel(web_channel_info, db)
            record['web_channel_id']: int | None = web_channel.id if web_channel else None

        # Process the show record
        show_repo: ShowRepository = ShowRepository()
        show: Show | None = show_repo.create_show(record, db)
        show_id: int | None = show.id if show else None

        # Process show genres
        genres: list[str] = record.get('genres', [])

        if genres:
            genre_service = GenreService()
            for genre_name in genres:
                genre: Genre | None = genre_service.get_or_create_genre(genre_name, db)
                genre_id: int | None = genre.id if genre else None

                show_genre_service: ShowGenreService = ShowGenreService()
                # noinspection PyUnusedLocal
                show_genre: ShowGenre | None = show_genre_service.create_show_genre(show_id, genre_id, db)

        # Process show seasons
        season_service = SeasonService()
        seasons = season_service.fetch_season_index_page(record.get('id'))

        if seasons:
            for record in seasons:
                # noinspection PyUnusedLocal
                season = season_service.process_season_record(record, show_id, db)

        # Process show episodes
        episode_service = EpisodeService()
        episodes = episode_service.fetch_episode_index_page(record.get('id'))

        if episodes:
            for episode in episodes:
                # noinspection PyUnusedLocal
                episode = episode_service.process_episode_record(episode, show_id, db)
