"""Repository for network data."""

import logging
from sqlalchemy import select, Select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from bingefriend.shows.core.models.network import Network


# noinspection PyMethodMayBeStatic
class NetworkRepository:
    """Repository for network data."""

    def get_network_by_maze_id(self, maze_id: int, db: Session) -> Network | None:
        """Get a network by its ID.

        Args:
            maze_id (int): The ID of the network to be fetched.
            db (Session): The database session to use.

        Returns:
            Network | None: The network object if found, else None.

        """
        network: Network | None = None

        query: Select = select(Network).where(Network.maze_id == maze_id)

        try:
            network = db.execute(query).scalars().first()
        except Exception as e:
            logging.error(f"Error fetching network by maze_id {maze_id}: {e}")
            network = None
        finally:
            return network

    def create_network(self, network_data: dict, db: Session) -> Network | None:
        """Create a new network entry in the database.

        Args:
            network_data (dict): Data of the network to be created.
            db (Session): The database session to use.

        Returns:
            Network | None: The created network object if successful, else None.

        """
        network: Network | None = None

        try:
            country_data: dict = network_data.get('country') or {}

            network = Network(
                maze_id=network_data.get('id'),
                name=network_data.get('name'),
                country_name=country_data.get('name'),
                country_timezone=country_data.get('timezone'),
                country_code=country_data.get('code')
            )
            db.add(network)
            db.flush()
            logging.info(f"Network created with ID {network.id}")
        except IntegrityError as e:
            try:
                logging.warning(f"Re-fetching network maze_id {network_data.get('id')} due to IntegrityError: {e}")
                network = self.get_network_by_maze_id(network_data.get('id'), db)
            except SQLAlchemyError as e:
                logging.error(f"Error fetching network maze_id {network_data.get('id')} after IntegrityError: {e}")
                network = None
        except SQLAlchemyError as e:
            logging.error(f"Error creating network maze_id {network_data.get('id')}: {e}")
            network = None
        except Exception as e:
            logging.error(f"Unexpected error for network maze_id {network_data.get('id')}: {e}")
            network = None
        finally:
            return network
