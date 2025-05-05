"""Repository for genre data."""

import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.genre import Genre


# noinspection PyMethodMayBeStatic
class GenreRepository:
    """Repository for genre data."""

    def get_genre_by_name(self, name: str, db: Session) -> Genre | None:
        """Get a genre by its name."

        Args:
            name (str): The name of the genre.
            db (Session): The database session to use.

        Returns:
            int | None: The ID of the genre if found, otherwise None.

        """
        genre: Genre | None = None

        try:
            query = db.query(Genre).filter(Genre.name == name)
            genre = db.execute(query).scalars().first()
        except Exception as e:
            logging.error(f"Error fetching genre by name {name}: {e}")
            genre = None
        finally:
            return genre

    def create_genre(self, name: str, db: Session) -> Genre | None:
        """Create a new genre entry in the database.

        Args:
            name (str): The name of the genre to be created.
            db (Session): The database session to use.

        Returns:
            Genre | None: The created genre object if successful, else None.

        """

        genre: Genre | None = None

        try:
            genre = Genre(name=name)
            db.add(genre)
            db.flush()
            logging.info(f"Genre created with ID {genre.id}")
        except IntegrityError as e:
            try:
                logging.warning(f"Re-fetching genre {name} due to IntegrityError: {e}")
                genre = self.get_genre_by_name(name, db)
            except Exception as e:
                logging.error(f"Error fetching genre by name {name} after IntegrityError: {e}")
                genre = None
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError while creating genre {name}: {e}")
            genre = None
        except Exception as e:
            print(f"Error creating genre {name}: {e}")
            genre = None
        finally:
            return genre
