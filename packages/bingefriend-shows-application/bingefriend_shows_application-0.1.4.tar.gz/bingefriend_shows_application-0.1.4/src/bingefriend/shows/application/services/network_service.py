"""Service to manage network-related operations."""
import logging
from sqlalchemy.orm import Session
from bingefriend.shows.application.repositories.network_repo import NetworkRepository


# noinspection PyMethodMayBeStatic
class NetworkService:
    """Service to manage network-related operations."""

    def get_or_create_network(self, network_data: dict | None, db: Session) -> int | None:
        """Get or create a network entry using an atomic approach.

        Attempts to fetch the network by maze_id. If not found, attempts
        an INSERT IGNORE and then fetches the ID again.

        Args:
            network_data (dict | None): Data of the network including 'id' (maze_id).
            db (Session): The database session.

        Returns:
            int | None: The primary key (internal DB ID) of the network, or None if data is invalid or an error occurs.
        """
        if not network_data:
            logging.debug("No network data provided to get_or_create_network.")
            return None

        network_maze_id = network_data.get('id')
        if not network_maze_id:
            logging.warning("Network data provided but missing 'id' (maze_id).")
            return None

        network_repo = NetworkRepository()

        # 1. First attempt to get the network PK
        network_pk = network_repo.get_network_pk_by_maze_id(network_maze_id, db)
        if network_pk:
            logging.debug(f"Found existing network PK {network_pk} for maze_id {network_maze_id}.")
            return network_pk

        # 2. If not found, attempt to create using INSERT IGNORE
        logging.debug(f"Network maze_id {network_maze_id} not found. Attempting create.")
        created_attempted = network_repo.create_network_if_not_exists(network_data, db)

        if not created_attempted:
            # Logged within create_network_if_not_exists
            logging.error(f"Failed to execute INSERT IGNORE for network maze_id {network_maze_id}.")
            return None  # Indicate failure

        # 3. Regardless of whether the INSERT IGNORE added a row or was ignored,
        #    the network *should* exist now. Fetch its PK again.
        #    A flush might be needed here IF the INSERT IGNORE was executed by the ORM
        #    and we needed to read via the ORM immediately. But since we used Core execute
        #    and are re-querying, it should be visible within the transaction.
        #    If issues persist, uncommenting the flush might help, but test first.
        # try:
        #     db.flush() # Ensure the INSERT IGNORE is sent to DB before re-querying
        # except Exception as flush_err:
        #     logging.error(
        #       f"Error flushing session after INSERT IGNORE attempt for maze_id {network_maze_id}: {flush_err}"
        #     )
        # Decide how to handle flush errors - maybe return None

        network_pk = network_repo.get_network_pk_by_maze_id(network_maze_id, db)

        if network_pk:
            logging.debug(f"Retrieved network PK {network_pk} for maze_id {network_maze_id} after create attempt.")
            return network_pk
        else:
            # This case should ideally not happen if create_network_if_not_exists succeeded
            # unless there's a deeper transaction visibility issue or the insert failed silently.
            logging.error(
                f"Failed to retrieve network PK for maze_id {network_maze_id} even after INSERT IGNORE attempt.")
            return None
