"""Service to manage network-related operations."""

from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.network_repo import NetworkRepository
from bingefriend.shows.core.models import Network


# noinspection PyMethodMayBeStatic
class NetworkService:
    """Service to manage network-related operations."""

    def get_or_create_network(self, network_data: dict, db: Session) -> Network | None:
        """Get or create a network entry in the database.

        Args:
            network_data (dict): Data of the network to be created or fetched.
            db (Session): The database session to use.

        Returns:
            Network | None: The network object if it exists or is created, else None.
        """

        network_repo: NetworkRepository = NetworkRepository()

        maze_id: int = network_data.get('id')

        if not maze_id:
            return None

        network: Network | None = network_repo.get_network_by_maze_id(maze_id, db)

        if not network:
            network = network_repo.create_network(network_data, db)

        return network
