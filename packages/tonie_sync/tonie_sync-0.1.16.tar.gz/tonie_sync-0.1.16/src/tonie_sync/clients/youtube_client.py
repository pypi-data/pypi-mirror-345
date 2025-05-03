import logging
import os
import re
from pathlib import Path

from pytubefix import Playlist, YouTube

from ..models import YoutubeTrackMetadata


class YoutubeClient:
    """Wrapper for the Youtube library pytubefix."""

    _spotdl = None

    def __init__(
        self,
        target_directory: Path = Path("media"),
    ):
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        self.target_directory = target_directory
        self._logger = logging.getLogger(__name__)

    def search_and_download(self, query: list[str] | str) -> list[YoutubeTrackMetadata]:
        """Search for songs on Youtube and download them.

        Args:
        ----
            query: The search query to find songs on Youtube.

        Returns:
        -------
            list[YoutubeTrackMetadata]: A list of YoutubeTrackMetadata objects for the downloaded songs.

        Example:
        -------
            >>> client.search_and_download("https://youtube.com/playlist?list=OLAK5uy_kP41f7I4coTZ1yh9G_FyQrJSFiS4eQQgw&si=wgQvRwuCBGgP5-Io")

        """
        if isinstance(query, str):
            queries = [query]
        else:
            queries = queries
        for query in queries:
            is_playlist = re.match(r"^.*\.(com|be)/playlist\?list=.*$", query)
            tracks_metadata: list[YoutubeTrackMetadata] = []
            if is_playlist:
                pl = Playlist(query)
                for track in pl.videos:
                    track_metadata = YoutubeTrackMetadata(
                        artists=[track.author],
                        download_root=self.target_directory,
                        name=track.title,
                        duration_ms=track.length * 1000,  # convert to ms
                        album_name=None,
                        image_url=track.thumbnail_url,
                        release_year=track.publish_date.year if track.publish_date else None,
                        disc_number=None,
                        track_number=None,
                        id=track.video_id,
                        is_playable=True,  # always True for Youtube songs,
                        youtube_stream=track.streams.get_audio_only(),
                    )
                    tracks_metadata.append(track_metadata)
            else:
                track = YouTube(query)
                track_metadata = YoutubeTrackMetadata(
                    artists=[track.author],
                    download_root=self.target_directory,
                    name=track.title,
                    duration_ms=track.length * 1000,  # convert to ms
                    album_name=None,
                    image_url=track.thumbnail_url,
                    release_year=track.publish_date.year if track.publish_date else None,
                    disc_number=None,
                    track_number=None,
                    id=track.video_id,
                    is_playable=True,  # always True for Youtube songs
                    youtube_stream=track.streams.get_audio_only(),
                )
                tracks_metadata.append(track_metadata)
        for track_metadata in tracks_metadata:
            self._logger.info(f"Downloading {track.title} from Youtube")
            track_metadata.youtube_stream.download(
                output_path=track_metadata.download_root,
                filename=track_metadata.filename,
            )
        return tracks_metadata
