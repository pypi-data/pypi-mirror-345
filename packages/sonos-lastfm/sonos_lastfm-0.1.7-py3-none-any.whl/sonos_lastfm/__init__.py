"""Sonos Last.fm scrobbler package."""

from .cli import main
from .sonos_lastfm import SonosScrobbler

__version__ = "0.1.7"
__all__ = ["main", "SonosScrobbler"]
