from src.config import MAX_SEARCH_ITERATIONS
from src.graph import quality_router


def test_needs_more_search_and_under_cap_goes_to_search():
    state = {
        "need_more_search": True,
        "search_count": 1,
        "max_search_iterations": 5,
    }
    assert quality_router(state) == "search"


def test_needs_more_search_but_at_cap_goes_to_final():
    state = {
        "need_more_search": True,
        "search_count": 5,
        "max_search_iterations": 5,
    }
    assert quality_router(state) == "final"


def test_needs_more_search_but_over_cap_goes_to_final():
    state = {
        "need_more_search": True,
        "search_count": 6,
        "max_search_iterations": 5,
    }
    assert quality_router(state) == "final"


def test_does_not_need_more_search_goes_to_final():
    state = {
        "need_more_search": False,
        "search_count": 0,
        "max_search_iterations": 5,
    }
    assert quality_router(state) == "final"



