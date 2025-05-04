"""Repository for season data."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from bingefriend.shows.core.models.season import Season


# noinspection PyMethodMayBeStatic
class SeasonRepository:
    """Repository for season data."""

    def upsert_season(self, season_data: dict, show_id: int, db: Session) -> int | None:
        """Create a new season entry or update an existing one based on maze_id.

        Args:
            season_data (dict): Data of the season to be created or updated. Must include 'id' (maze_id).
            show_id (int): The internal DB ID of the show this season belongs to.
            db (Session): The database session.

        Returns:
            int | None: The primary key (internal DB ID) of the created/updated season, or None on error.
        """
        maze_id = season_data.get("id")
        # noinspection PyUnusedLocal
        season_id = None  # Initialize season_id

        if not maze_id:
            logging.error(f"Cannot upsert season for show_id {show_id}: 'id' (maze_id) is missing from season_data.")
            return None
        if not show_id:
            logging.error(f"Cannot upsert season for maze_id {maze_id}: show_id is missing.")
            return None

        try:
            # Look for existing season by maze_id AND show_id
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
                "show_id": show_id,
                "maze_id": maze_id,
                "url": season_data.get("url"),
                "number": season_data.get("number"),
                "name": season_data.get("name"),
                "episodeOrder": season_data.get("episodeOrder"),
                "premiereDate": db_premiere,
                "endDate": db_end,
                "image_medium": image_data.get("medium"),
                "image_original": image_data.get("original"),
                "summary": season_data.get("summary"),
            }

            if existing_season:
                logging.debug(
                    f"Updating existing season maze_id: {maze_id} for show_id: {show_id} (DB ID: {existing_season.id})")
                for key, value in season_attrs.items():
                    setattr(existing_season, key, value)
                season_id = existing_season.id
                logging.info(f"Successfully prepared update for season maze_id: {maze_id}, internal DB ID: {season_id}")

            else:
                logging.debug(f"Creating new season maze_id: {maze_id} for show_id: {show_id}")
                new_season = Season(**season_attrs)
                db.add(new_season)
                db.flush()  # <--- Add flush here
                season_id = new_season.id  # Read ID after flush
                if season_id:
                    logging.info(f"Successfully created season maze_id: {maze_id}, internal DB ID: {season_id}")
                else:
                    logging.error(f"Failed to retrieve generated ID for new season maze_id: {maze_id} after flush.")
                    # Consider rollback if needed based on transaction strategy
                    # db.rollback()
                    return None  # Return None if ID retrieval failed

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError upserting season maze_id {maze_id} for show_id {show_id}: {e}")
            # db.rollback()
            return None
        except Exception as e:
            logging.error(f"Unexpected error upserting season maze_id {maze_id} for show_id {show_id}: {e}",
                          exc_info=True)
            # db.rollback()
            return None

        return season_id

    def get_season_id_by_show_id_and_number(self, show_id: int, season_number: int, db: Session) -> int | None:
        """Get the internal season ID using the show ID and season number."""
        if not show_id or season_number is None:
            logging.warning("Attempted get_season_id with missing show_id or season_number.")
            return None
        try:
            season_id = db.query(Season.id).filter(
                Season.show_id == show_id,
                Season.number == season_number
            ).scalar()
            return season_id
        except SQLAlchemyError as e:
            logging.error(f"Error fetching season ID for show_id {show_id}, season_number {season_number}: {e}")
            return None
        except Exception as e:
            logging.error(
                f"Unexpected error fetching season ID for show_id {show_id}, season_number {season_number}: {e}")
            return None
