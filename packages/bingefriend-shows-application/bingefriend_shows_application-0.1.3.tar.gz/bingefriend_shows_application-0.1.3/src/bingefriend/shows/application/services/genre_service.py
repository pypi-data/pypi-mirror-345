"""Service to manage genre-related operations."""

import logging
from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.genre_repo import GenreRepository


# noinspection PyMethodMayBeStatic
class GenreService:
    """Service to manage genre-related operations."""

    def get_or_create_genre(self, genre_name: str | None, db: Session) -> int | None:
        """Get or create a genre entry using an atomic approach.

        Attempts to fetch the genre by name. If not found, attempts
        an INSERT IGNORE and then fetches the ID again.

        Args:
            genre_name (str | None): Name of the genre to be created or fetched.
            db (Session): SQLAlchemy session object.

        Returns:
            int | None: The primary key (internal DB ID) of the genre, or None if name is invalid or an error occurs.
        """
        if not genre_name:
            logging.debug("No genre name provided to get_or_create_genre.")
            return None

        genre_repo = GenreRepository()

        # 1. First attempt to get the genre PK
        genre_pk = genre_repo.get_genre_pk_by_name(genre_name, db)
        if genre_pk:
            logging.debug(f"Found existing genre PK {genre_pk} for name '{genre_name}'.")
            return genre_pk

        # 2. If not found, attempt to create using INSERT IGNORE
        logging.debug(f"Genre name '{genre_name}' not found. Attempting create.")
        created_attempted = genre_repo.create_genre_if_not_exists(genre_name, db)

        if not created_attempted:
            # Logged within create_genre_if_not_exists
            logging.error(f"Failed to execute INSERT IGNORE for genre name '{genre_name}'.")
            return None  # Indicate failure

        # 3. Regardless of whether the INSERT IGNORE added a row or was ignored,
        #    the genre *should* exist now. Fetch its PK again.
        genre_pk = genre_repo.get_genre_pk_by_name(genre_name, db)

        if genre_pk:
            logging.debug(f"Retrieved genre PK {genre_pk} for name '{genre_name}' after create attempt.")
            return genre_pk
        else:
            # This case should ideally not happen if create_genre_if_not_exists succeeded
            logging.error(
                f"Failed to retrieve genre PK for name '{genre_name}' even after INSERT IGNORE attempt.")
            return None
