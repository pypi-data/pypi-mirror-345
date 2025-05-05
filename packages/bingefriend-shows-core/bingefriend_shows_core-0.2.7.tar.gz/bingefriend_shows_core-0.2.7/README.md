# BingeFriend Shows Core

This package provides SQLAlchemy models for storing TV show data, such as shows, seasons, networks, etc., primarily sourced from the TVMaze API.

## Purpose

Core data structures (database models) for the BingeFriend application suite related to TV shows.

## Requirements

* Python >= 3.11
* SQLAlchemy >= 2.0

## Models

Includes models for:
* Show
* Season
* Episode
* Network
* Genre

## Installation

*(Add installation instructions if this package will be distributed, e.g., via pip)*

```bash
# Example pip installation
pip install bingefriend-shows-core
```

## Usage

Import the models into your application to interact with the database via SQLAlchemy.

```python
from binge_friend.shows.core.models import Show, Season # etc.
# ... SQLAlchemy session setup ...

# Example query
# new_season = Season(maze_id=123, number=1, show_id=1)
# session.add(new_season)
# session.commit()
```

License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.