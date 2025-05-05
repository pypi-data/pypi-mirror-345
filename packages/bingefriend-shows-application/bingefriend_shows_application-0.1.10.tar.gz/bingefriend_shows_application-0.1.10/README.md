# BingeFriend Shows Package

This package manages TV show data within the BingeFriend application. It handles fetching data from an external API (TVMaze), processing it, and storing it in the database.

## Installation

```bash
pip install bingefriend-shows-application
```

## Core Components

*   **`ShowService`**: Orchestrates the fetching and processing of show data, including details, seasons, and episodes. Manages show updates.
*   **`GenreService`**: Manages genre information, retrieving or creating genres as needed.
*   **`NetworkService`**: Handles TV network data associated with shows.
*   **`WebChannelService`**: Manages web channel data associated with shows.
*   **`SeasonService`**: Fetches and processes season information for shows.
*   **`EpisodeService`**: Fetches and processes episode information for shows.
*   **`ShowGenreService`**: Manages the relationship between shows and genres.
*   **Repositories (`*_repo.py`)**: Handle database interactions for each entity (Show, Genre, Network, etc.).

## Functionality

*   Fetches show index pages and individual show details from the TVMaze API.
*   Processes show records, creating or updating shows and their related entities (genres, networks, web channels, seasons, episodes) in the database.
*   Synchronizes genres associated with each show.
*   Fetches and processes updates for existing shows.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details. Copyright (c) 2025 Tom Boone.