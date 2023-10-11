import pytest

from src.apis import get_media_expert_data


@pytest.asyncio
def test_get_media_expert_data():
    results = get_media_expert_data()
    assert len(results) == 4
