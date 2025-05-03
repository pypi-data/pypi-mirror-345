import logging
import os
import re

from tonie_sync.clients.youtube_client import YoutubeClient

from .clients import SpotDLClientFactory, TonieClient


class SyncService:
    """Responsible for syncing music from Spotify to a Toniebox."""

    def __init__(
        self,
        spotify_client_id: str | None = None,
        spotify_client_secret: str | None = None,
        tonie_username: str | None = None,
        tonie_password: str | None = None,
        tonie_household: str | None = None,
        target_directory: str = "./downloads/tonie_sync",
    ) -> None:
        self.spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID", spotify_client_id)
        self.spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", spotify_client_secret)
        self.tonie_username = os.environ.get("TONIE_USERNAME", tonie_username)
        self.tonie_password = os.environ.get("TONIE_PASSWORD", tonie_password)
        self.tonie_household = os.environ.get("TONIE_HOUSEHOLD", tonie_household)
        self.target_directory = os.environ.get("TARGET_DIRECTORY", target_directory)
        if not self.target_directory:
            self.target_directory = os.path.join(os.path.expanduser("~"), "Downloads", "tonie_sync")

    def sync(self, creative_tonie_name: str, query: str):
        """Sync music from Spotify to a Toniebox.

        Args:
        ----
            creative_tonie_name: The name of the creative Tonie.
            query: The search query to find songs on Spotify or Youtube.

        """
        tonie_client = TonieClient(
            email=self.tonie_username,  # type: ignore
            password=self.tonie_password,  # type: ignore
            household=self.tonie_household,  # type: ignore
        )

        if not os.path.exists(self.target_directory):
            logging.info(f"Creating download folder {self.target_directory}")
            os.makedirs(self.target_directory)

        is_youtube_query = re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/", query)
        if is_youtube_query:
            youtube_client = YoutubeClient(
                target_directory=self.target_directory,  # type: ignore
            )
            logging.info("Downloading from YouTube")
            download_tracks_metadata = youtube_client.search_and_download(query=query)
        else:
            logging.info("Downloading from Spotify")
            spotify_client = SpotDLClientFactory.create(
                client_id=self.spotify_client_id,  # type: ignore
                client_secret=self.spotify_client_secret,  # type: ignore
                target_directory=self.target_directory,  # type: ignore
            )
            download_tracks_metadata = spotify_client.search_and_download(query=query)

        tonie_client.update_creative_tonie(creative_tonie_name, download_tracks_metadata)
