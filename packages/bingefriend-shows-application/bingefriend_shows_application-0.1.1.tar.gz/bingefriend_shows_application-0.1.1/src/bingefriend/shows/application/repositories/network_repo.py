"""Repository for network data."""

import logging
from bingefriend.shows.core.models.network import Network
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError  # More specific catch if needed


# noinspection PyMethodMayBeStatic
class NetworkRepository:
    """Repository for network data."""

    def get_network_pk_by_maze_id(self, maze_id: int, db: Session) -> int | None:
        """Get a network's primary key by its maze_id.

        Args:
            maze_id (int): The maze_id of the network to be fetched.
            db (Session): The database session.

        Returns:
            int | None: The primary key of the network if it exists, else None.
        """
        try:
            # Query for the primary key directly for efficiency
            network_pk = db.query(Network.id).filter(Network.maze_id == maze_id).scalar()
            return network_pk
        except SQLAlchemyError as e:
            logging.error(f"Error fetching network PK by maze_id {maze_id}: {e}")
            return None
        except Exception as e:  # Catch broader exceptions if necessary
            logging.error(f"Unexpected error fetching network PK by maze_id {maze_id}: {e}")
            return None

    def create_network_if_not_exists(self, network_data: dict, db: Session) -> bool:
        """Attempt to create a new network using INSERT IGNORE.

        Args:
            network_data (dict): Data of the network to be created.
            db (Session): The database session.

        Returns:
            bool: True if the operation succeeded (insert attempted), False otherwise.
                  Note: This doesn't guarantee a new row was inserted, only that
                  the command was executed without raising an exception here.
        """
        network_maze_id = network_data.get('id')
        if not network_maze_id:
            logging.warning("Attempted to create network with missing 'id' in data.")
            return False

        logging.debug(f"Attempting INSERT IGNORE for network maze_id: {network_maze_id}")
        try:
            country_data = network_data.get('country') or {}
            insert_stmt = mysql_insert(Network).values(
                maze_id=network_maze_id,
                name=network_data.get('name'),
                country_name=country_data.get('name'),
                country_timezone=country_data.get('timezone'),
                country_code=country_data.get('code')
            ).prefix_with('IGNORE')  # Add the IGNORE prefix for MySQL

            db.execute(insert_stmt)
            # We don't commit here, just execute within the ongoing transaction.
            # We also don't need db.flush() as we aren't relying on the ORM object's state.
            logging.debug(f"Executed INSERT IGNORE for network maze_id: {network_maze_id}")
            return True  # Indicate the operation was attempted

        except SQLAlchemyError as e:
            # Catch potential errors during statement execution, though IGNORE
            # should prevent IntegrityError for duplicates.
            logging.error(f"SQLAlchemyError during INSERT IGNORE for network maze_id {network_maze_id}: {e}")
            # Consider rolling back specific errors if needed, but often the main activity handles rollback.
            return False
        except Exception as e:
            logging.error(f"Unexpected error during INSERT IGNORE for network maze_id {network_maze_id}: {e}")
            return False
