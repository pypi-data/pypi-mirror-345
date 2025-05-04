"""Repository for genre data."""

import logging
from bingefriend.shows.core.models.genre import Genre
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError


# noinspection PyMethodMayBeStatic
class GenreRepository:
    """Repository for genre data."""

    def get_genre_pk_by_name(self, name: str, db: Session) -> int | None:
        """Get a genre's primary key by its name.

        Args:
            name (str): The name of the genre to be fetched.
            db (Session): The database session.

        Returns:
            int | None: The primary key of the genre if it exists, else None.
        """
        if not name:
            logging.warning("Attempted to get genre PK with empty name.")
            return None
        try:
            # Query for the primary key directly for efficiency
            genre_pk = db.query(Genre.id).filter(Genre.name == name).scalar()
            return genre_pk
        except SQLAlchemyError as e:
            logging.error(f"Error fetching genre PK by name '{name}': {e}")
            return None
        except Exception as e:  # Catch broader exceptions if necessary
            logging.error(f"Unexpected error fetching genre PK by name '{name}': {e}")
            return None

    def create_genre_if_not_exists(self, name: str, db: Session) -> bool:
        """Attempt to create a new genre using INSERT IGNORE.

        Args:
            name (str): Name of the genre to be created.
            db (Session): The database session.

        Returns:
            bool: True if the operation succeeded (insert attempted), False otherwise.
                  Note: This doesn't guarantee a new row was inserted.
        """
        if not name:
            logging.warning("Attempted to create genre with empty name.")
            return False

        logging.debug(f"Attempting INSERT IGNORE for genre name: '{name}'")
        try:
            insert_stmt = mysql_insert(Genre).values(
                name=name
            ).prefix_with('IGNORE')  # Add the IGNORE prefix for MySQL

            db.execute(insert_stmt)
            logging.debug(f"Executed INSERT IGNORE for genre name: '{name}'")
            return True  # Indicate the operation was attempted

        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError during INSERT IGNORE for genre name '{name}': {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during INSERT IGNORE for genre name '{name}': {e}")
            return False
