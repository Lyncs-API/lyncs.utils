from lyncs_utils import isiterable, single_true, interactive


def test_isiterable():
    assert isiterable([])
    assert isiterable(map(lambda _: _, []))
    assert isiterable([1, 2, 3], int)
    assert not isiterable(1)
    assert not isiterable([1, 2, 3], (str, float))


def test_single_true():
    assert single_true([1])
    assert single_true([1, 0, 0, 0])
    assert single_true([True, False, 0, 0])
    assert not single_true([False, True, False, True])
    assert not single_true(
        [
            False,
        ]
    )


def test_interactive():
    assert not interactive()
