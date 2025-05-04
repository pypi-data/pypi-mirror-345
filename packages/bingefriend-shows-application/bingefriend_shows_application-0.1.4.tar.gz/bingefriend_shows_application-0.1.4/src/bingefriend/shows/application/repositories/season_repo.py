"""Repository for managing seasons in the database."""
import logging
from typing import Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.season import Season


# noinspection PyMethodMayBeStatic
class SeasonRepository:
    """Repository to handle season-related database operations."""

    def create_season(self, season_data: dict, db: Session) -> Season | None:
        """Create a new season entry in the database.

        Args:
            season_data (dict): A dictionary containing season data.
            db (Session): The database session to use for the operation.

        Returns:
            Season: The created season object.

        """
        image_data = season_data.get("image") or {}

        try:
            season = Season(
                maze_id=season_data.get("id"),
                url=season_data.get("url"),
                number=season_data.get("number"),
                name=season_data.get("name"),
                episodeOrder=season_data.get("episodeOrder"),
                premiereDate=season_data.get("premiereDate"),
                endDate=season_data.get("endDate"),
                network_id=season_data.get("network_id"),
                webChannel_id=season_data.get("web_channel_id"),
                image_medium=image_data.get("medium"),
                image_original=image_data.get("original"),
                summary=season_data.get("summary"),
                show_id=season_data.get("show_id")
            )

            db.add(season)

        except Exception as e:
            print(f"Error creating season entry: {e}")

            return None

        return season

    def get_season_id_by_show_id_and_number(self, show_id: int, season_number: int, db: Session) -> int | None:
        """Get the season ID for a given show ID and season number.

        Args:
            show_id (int): The ID of the show.
            season_number (int): The season number.
            db (Session): The database session to use for the operation.

        """
        try:
            season: Season | None = db.query(Season).filter(
                Season.show_id == show_id,
                Season.number == season_number
            ).first()
        except Exception as e:
            print(f"Error fetching season ID: {e}")
            return None

        if not season:
            return None

        return season.id

    def upsert_season(self, season_data: dict[str, Any], db: Session) -> Optional[int]:
        """Creates a new season or updates an existing one based on maze_id and show_id.

        Args:
            season_data (dict[str, Any]): A dictionary containing season data from the API.
                                          It's expected that 'show_id' (internal DB ID)
                                          and potentially 'network_id' have been added
                                          to this dict by the calling service.
            db (Session): The database session to use for the operation.

        Returns:
            Optional[int]: The internal database ID of the created/updated season,
                           or None if an error occurred or identifiers were missing.
        """
        maze_id = season_data.get("id")
        show_id = season_data.get("show_id")

        season_id = None

        if not maze_id:
            logging.error("Cannot upsert season: 'id' (maze_id) is missing from season_data.")
            return None
        if not show_id:
            logging.error(f"Cannot upsert season maze_id {maze_id}: 'show_id' is missing from season_data.")
            return None

        try:
            existing_season = db.query(Season).filter(
                Season.maze_id == maze_id,
                Season.show_id == show_id
            ).first()

            premiere_date = season_data.get('premiereDate')
            end_date = season_data.get('endDate')
            db_premiere = premiere_date if premiere_date else None
            db_end = end_date if end_date else None
            image_data = season_data.get("image") or {}

            season_attrs = {
                "maze_id": maze_id,
                "show_id": show_id,
                "url": season_data.get("url"),
                "number": season_data.get("number"),
                "name": season_data.get("name"),
                "episodeOrder": season_data.get("episodeOrder"),
                "premiereDate": db_premiere,
                "endDate": db_end,
                "network_id": season_data.get("network_id"),
                "webChannel_id": season_data.get("web_channel_id"),
                "image_medium": image_data.get("medium"),
                "image_original": image_data.get("original"),
                "summary": season_data.get("summary"),
            }

            if existing_season:
                logging.debug(
                    f"Updating existing season with maze_id: {maze_id} for show_id: {show_id} (DB ID: "
                    f"{existing_season.id})"
                )
                update_data = season_attrs
                for key, value in update_data.items():
                    setattr(existing_season, key, value)
                season_id = existing_season.id
                logging.debug(f"Successfully updated season maze_id: {maze_id}, internal DB ID: {season_id}")
            else:
                logging.debug(f"Creating new season with maze_id: {maze_id} for show_id: {show_id}")
                new_season = Season(**season_attrs)
                db.add(new_season)
                db.flush()
                season_id = new_season.id
                logging.debug(f"Successfully created season maze_id: {maze_id}, internal DB ID: {season_id}")

            return season_id

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError upserting season entry for maze_id {maze_id}, show_id {show_id}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error upserting season entry for maze_id {maze_id}, show_id {show_id}: {e}",
                          exc_info=True)
            return None
        finally:
            return season_id
