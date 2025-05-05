"""Repository for show-genre data."""

import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.show_genre import ShowGenre


# noinspection PyMethodMayBeStatic
class ShowGenreRepository:
    """Repository for show-genre data."""

    def create_show_genre(self, show_id: int, genre_id: int, db: Session) -> ShowGenre | None:
        """Create a new show-genre entry in the database.

        Args:
            show_id (int): The ID of the show.
            genre_id (int): The ID of the genre.
            db (Session): The database session to use.

        Returns:
            ShowGenre | None: The created show-genre object if successful, else None.

        """
        show_genre: ShowGenre | None = None

        try:
            show_genre = ShowGenre(show_id=show_id, genre_id=genre_id)
            db.add(show_genre)
            db.flush()
            logging.info(f"Show-genre created with ID {show_genre.id}")
        except IntegrityError as e:
            logging.warning(f"Show-genre entry already exists for show_id {show_id} and genre_id {genre_id}: {e}")
            show_genre = None
        except Exception as e:
            logging.error(f"Error creating show-genre for show_id {show_id} and genre_id {genre_id}: {e}")
            show_genre = None
        finally:
            return show_genre
