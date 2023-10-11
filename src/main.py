import logging

from .apis import get_media_expert_data


_logger = logging.getLogger(__name__)


def main() -> int:
    get_media_expert_data()

    return 0
