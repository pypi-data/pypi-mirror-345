from datetime import date

import pytest
from pydantic import ValidationError

from metaboatrace.models.stadium import (
    Event,
    EventHolding,
    EventHoldingStatus,
    SeriesGrade,
    SeriesKind,
    StadiumTelCode,
)


@pytest.mark.parametrize(
    "stadium_tel_code,starts_on,days,grade,kind,title,expected",
    [
        (
            StadiumTelCode.KIRYU,
            date.today(),
            5,
            SeriesGrade.SG,
            SeriesKind.ALL_LADIES,
            "Test Event",
            True,
        ),  # valid case
        (
            StadiumTelCode.KIRYU,
            date.today(),
            2,
            SeriesGrade.SG,
            SeriesKind.ALL_LADIES,
            "Test Event",
            False,
        ),  # invalid days
        (
            StadiumTelCode.KIRYU,
            date.today(),
            10,
            SeriesGrade.SG,
            SeriesKind.ALL_LADIES,
            "Test Event",
            False,
        ),  # invalid days
    ],
)
def test_event(stadium_tel_code, starts_on, days, grade, kind, title, expected):  # type: ignore
    data = {
        "stadium_tel_code": stadium_tel_code,
        "starts_on": starts_on,
        "days": days,
        "grade": grade,
        "kind": kind,
        "title": title,
    }
    if expected:
        Event(**data)
    else:
        with pytest.raises(ValidationError):
            Event(**data)


@pytest.mark.parametrize(
    "stadium_tel_code,date,status,progress_day,should_raise_error",
    [
        (
            StadiumTelCode.KIRYU,
            date.today(),
            EventHoldingStatus.OPEN,
            3,
            False,
        ),  # Valid case for OPEN status
        (
            StadiumTelCode.TODA,
            date.today(),
            EventHoldingStatus.CANCELED,
            None,
            False,
        ),  # Valid case for CANCELED status
        (
            StadiumTelCode.EDOGAWA,
            date.today(),
            EventHoldingStatus.OPEN,
            -1,
            False,
        ),  # Valid case: OPEN status and progress_day is -1
        (
            StadiumTelCode.HEIWAJIMA,
            date.today(),
            EventHoldingStatus.OPEN,
            None,
            True,
        ),  # Invalid case: OPEN status but no progress_day
        (
            StadiumTelCode.TAMAGAWA,
            date.today(),
            EventHoldingStatus.OPEN,
            8,
            True,
        ),  # Invalid progress_day value
        (
            StadiumTelCode.HAMANAKO,
            date.today(),
            EventHoldingStatus.POSTPONED,
            3,
            True,
        ),  # Invalid: progress_day provided for non-OPEN status
    ],
)
def test_event_holding(stadium_tel_code, date, status, progress_day, should_raise_error):  # type: ignore
    data = {
        "stadium_tel_code": stadium_tel_code,
        "date": date,
        "status": status,
        "progress_day": progress_day,
    }
    if should_raise_error:
        with pytest.raises(ValidationError):
            EventHolding(**data)
    else:
        event_holding = EventHolding(**data)
        assert event_holding.stadium_tel_code == stadium_tel_code
        assert event_holding.date == date
        assert event_holding.status == status
        assert event_holding.progress_day == progress_day
