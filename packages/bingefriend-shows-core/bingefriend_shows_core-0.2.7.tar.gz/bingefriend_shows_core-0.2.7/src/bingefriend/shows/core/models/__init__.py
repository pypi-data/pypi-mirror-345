"""SQLAlchemy models for the BingeFriend application."""

from bingefriend.shows.core.models.base import Base
from bingefriend.shows.core.models.show import Show
from bingefriend.shows.core.models.season import Season
from bingefriend.shows.core.models.episode import Episode
from bingefriend.shows.core.models.network import Network
from bingefriend.shows.core.models.web_channel import WebChannel
from bingefriend.shows.core.models.genre import Genre
from bingefriend.shows.core.models.show_genre import ShowGenre

__all__ = ["Base", "Show", "Season", "Episode", "Network", "WebChannel", "Genre", "ShowGenre"]
