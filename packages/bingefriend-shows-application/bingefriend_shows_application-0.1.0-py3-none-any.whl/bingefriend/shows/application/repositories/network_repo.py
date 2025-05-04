"""Repository for network data."""

from bingefriend.shows.core.models.network import Network
from sqlalchemy.orm import Session


# noinspection PyMethodMayBeStatic
class NetworkRepository:
    """Repository for network data."""

    def get_network_by_id(self, network_id, db: Session) -> int | None:
        """Get a network by its ID.

        Args:
            network_id (int): The ID of the network to be fetched.
            db (Session): The database session.

        Returns:
            int | None: The primary key of the network if it exists, else None.

        """

        try:
            network: Network | None = db.query(Network).filter(Network.maze_id == network_id).first()
        except Exception as e:
            print(f"Error fetching network by ID: {e}")
            return None

        if not network:
            return None

        network_pk = network.id

        return network_pk

    def create_network(self, network_data, db: Session) -> int | None:
        """Create a new network entry in the database.

        Args:
            network_data (dict): Data of the network to be created.
            db (Session): The database session.

        Returns:
            int | None: The primary key of the network if created successfully, else None.

        """

        try:
            country_data = network_data.get('country') or {}

            network = Network(
                maze_id=network_data.get('id'),
                name=network_data.get('name'),
                country_name=country_data.get('name'),
                country_timezone=country_data.get('timezone'),
                country_code=country_data.get('code')
            )

            db.add(network)

            network_pk = network.id
        except Exception as e:
            print(f"Error creating network entry: {e}")
            return None

        return network_pk
