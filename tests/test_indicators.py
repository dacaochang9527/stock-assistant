from stock_assistant.indicators import expma, is_limit_up, moving_average, rolling_max


def test_moving_average():
    assert moving_average([1, 2, 3, 4], 2) == [None, 1.5, 2.5, 3.5]


def test_expma_length():
    assert len(expma([1, 2, 3], 2)) == 3


def test_is_limit_up():
    assert is_limit_up(9.98, 10.0)
    assert not is_limit_up(9.0, 10.0)


def test_rolling_max_excludes_current_when_shifted():
    assert rolling_max([1, 5, 3, 4], 2, shift=1) == [None, None, 5, 5]
