"""Repository for network data."""

import logging
from bingefriend.shows.core.models.network import Network
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError


# noinspection PyMethodMayBeStatic
class NetworkRepository:
    """Repository to interact with network data."""

    def get_network_pk_by_maze_id(self, maze_id: int, db: Session) -> int | None:
        """Get a network's primary key by its TV Maze ID."""
        if not maze_id:
            logging.warning("Attempted to get network PK with missing maze_id.")
            return None
        try:
            network_pk = db.query(Network.id).filter(Network.maze_id == maze_id).scalar()
            return network_pk
        except SQLAlchemyError as e:
            logging.error(f"Error fetching network PK by maze_id {maze_id}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching network PK by maze_id {maze_id}: {e}")
            return None

    def create_network_if_not_exists(self, network_data: dict, db: Session) -> bool:
        """Attempt to create a new network using INSERT IGNORE.

        Args:
            network_data (dict): Data of the network to be created, must include 'id' (maze_id).
            db (Session): The database session.

        Returns:
            bool: True if the INSERT IGNORE was executed, False otherwise.
        """
        network_maze_id = network_data.get('id')
        if not network_maze_id:
            logging.warning("Attempted to create network with missing 'id' (maze_id) in data.")
            return False

        logging.debug(f"Attempting INSERT IGNORE for network maze_id: {network_maze_id}")
        try:
            country_data = network_data.get('country') or {}
            # Use INSERT IGNORE
            insert_stmt = mysql_insert(Network).values(
                maze_id=network_maze_id,
                name=network_data.get('name'),
                country_name=country_data.get('name'),
                country_timezone=country_data.get('timezone'),
                country_code=country_data.get('code'),
            ).prefix_with('IGNORE')  # Add the IGNORE prefix

            db.execute(insert_stmt)
            db.flush()  # Ensure the statement is sent
            logging.debug(f"Executed INSERT IGNORE and flushed for network maze_id: {network_maze_id}")
            return True  # Indicate the operation was attempted

        except SQLAlchemyError as e:
            # Log the specific error, including deadlock info if present
            logging.error(f"SQLAlchemyError during INSERT IGNORE for network maze_id {network_maze_id}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during INSERT IGNORE for network maze_id {network_maze_id}: {e}")
            return False
