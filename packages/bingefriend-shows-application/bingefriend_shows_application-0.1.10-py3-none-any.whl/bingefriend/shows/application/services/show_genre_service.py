"""Service to manage genre-related operations."""

from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.show_genre_repo import ShowGenreRepository
from bingefriend.shows.core.models import ShowGenre


# noinspection PyMethodMayBeStatic
class ShowGenreService:
    """Service to manage show genres."""

    def create_show_genre(self, show_id: int, genre_id: int, db: Session) -> ShowGenre | None:
        """Get or create a show-genre entry in the database.

        Args:
            show_id (int): The ID of the show.
            genre_id (int): The ID of the genre.
            db (Session): The database session to use.

        Returns:
            ShowGenre | None: The show-genre object if it exists or is created, else None.

        """
        show_genre_repo: ShowGenreRepository = ShowGenreRepository()
        show_genre: ShowGenre | None = show_genre_repo.create_show_genre(show_id, genre_id, db)

        return show_genre
