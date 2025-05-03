import logging
import os
import sys

from .sync_service import SyncService

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)


def main(query: str, creative_tonie_name: str):
    """Sync the files to the creative tonie based on the configuration."""
    sync_service = SyncService()
    sync_service.sync(query=query, creative_tonie_name=creative_tonie_name)


if __name__ == "__main__":
    query = os.environ.get("QUERY")
    creative_tonie_name = os.environ.get("CREATIVE_TONIE")

    if not query or not creative_tonie_name:
        print("Please provide a query and a creative tonie name.")
        sys.exit(1)

    main(query=query, creative_tonie_name=creative_tonie_name)
