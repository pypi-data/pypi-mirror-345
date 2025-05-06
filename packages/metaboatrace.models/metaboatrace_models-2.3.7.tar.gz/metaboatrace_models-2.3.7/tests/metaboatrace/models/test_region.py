import pytest

from metaboatrace.models.region import Branch, BranchFactory, Prefecture, PrefectureFactory


@pytest.mark.parametrize(
    "name, expected",
    [
        ("北海道", Prefecture.HOKKAIDO),
        ("東京", Prefecture.TOKYO),
        ("沖縄", Prefecture.OKINAWA),
    ],
)
def test_prefecture_factory(name, expected):  # type: ignore
    assert PrefectureFactory.create(name) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("東京", Branch.TOKYO),
        ("福井", Branch.FUKUI),
    ],
)
def test_branch_factory(name, expected):  # type: ignore
    assert BranchFactory.create(name) == expected


def test_prefecture_factory_invalid():  # type: ignore
    with pytest.raises(ValueError):
        PrefectureFactory.create("InvalidPrefecture")


def test_branch_factory_invalid():  # type: ignore
    with pytest.raises(ValueError):
        BranchFactory.create("InvalidBranch")
        BranchFactory.create("InvalidBranch")
        BranchFactory.create("InvalidBranch")
        BranchFactory.create("InvalidBranch")
