"""Repository for managing seasons in the database."""

import logging
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.season import Season


# noinspection PyMethodMayBeStatic
class SeasonRepository:
    """Repository to handle season-related database operations."""

    def create_season(self, season_data: dict, db: Session) -> Season | None:
        """Create a new season entry in the database.

        Args:
            season_data (dict): A dictionary containing season data.
            db (Session): The database session to use.

        Returns:
            Season: The created season object.

        """
        season: Season | None = None

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
                image_medium=image_data.get("medium"),
                image_original=image_data.get("original"),
                summary=season_data.get("summary"),
                show_id=season_data.get("show_id")
            )
            db.add(season)
            db.flush()
            logging.info(f"Season created with ID {season.id}")
        except IntegrityError as e:
            logging.warning(f"Season entry already exists: {e}")
            season = None
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error creating season entry: {e}")
            season = None
        except Exception as e:
            logging.error(f"Error creating season entry: {e}")
            season = None
        finally:
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
        season: Season | None = None

        try:
            query: Select = select(Season).filter(Season.show_id == show_id, Season.number == season_number)
            season = db.execute(query).scalars().first()
        except Exception as e:
            logging.error(f"Error fetching season {season_number} for show_id {show_id}: {e}")
            season = None
        finally:
            return season
