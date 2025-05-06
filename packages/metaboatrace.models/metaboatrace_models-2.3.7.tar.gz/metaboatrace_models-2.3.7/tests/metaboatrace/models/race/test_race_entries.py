from datetime import date

import pytest
from pydantic import ValidationError

from metaboatrace.models.race import (
    BoatSetting,
    CircumferenceExhibitionRecord,
    RaceEntry,
    RaceRecord,
    StartExhibitionRecord,
    WinningTrick,
)
from metaboatrace.models.stadium import StadiumTelCode

base_data = {
    "race_holding_date": date.today(),
    "stadium_tel_code": StadiumTelCode.HEIWAJIMA,
    "race_number": 1,
}


def test_race_entry_valid():  # type: ignore
    valid_data = {
        **base_data,
        "pit_number": 3,
        "racer_registration_number": 1234,
        "is_absent": False,
        "motor_number": 10,
        "boat_number": 123,
    }
    entry = RaceEntry(**valid_data)  # type: ignore
    assert entry.pit_number == valid_data["pit_number"]
    assert entry.is_absent == valid_data["is_absent"]
    assert entry.motor_number == valid_data["motor_number"]
    assert entry.boat_number == valid_data["boat_number"]


@pytest.mark.parametrize(
    "pit_number,is_absent,motor_number,boat_number,expected",
    [
        (7, False, 10, 123, False),  # invalid pit_number
        (3, False, 0, 123, False),  # invalid motor_number
        (3, False, 10, 1000, False),  # invalid boat_number
    ],
)
def test_race_entry_invalid(pit_number, is_absent, motor_number, boat_number, expected):  # type: ignore
    data = {
        **base_data,
        "pit_number": pit_number,
        "is_absent": is_absent,
        "motor_number": motor_number,
        "boat_number": boat_number,
    }
    if expected:
        RaceEntry(**data)
    else:
        with pytest.raises(ValidationError):
            RaceEntry(**data)


def test_boat_setting_valid():  # type: ignore
    valid_data = {
        **base_data,
        "pit_number": 3,
        "tilt": 2.5,
        "is_new_propeller": True,
        "motor_parts_exchanges": [],
    }
    setting = BoatSetting(**valid_data)  # type: ignore
    assert setting.pit_number == valid_data["pit_number"]
    assert setting.tilt == valid_data["tilt"]
    assert setting.is_new_propeller == valid_data["is_new_propeller"]
    assert setting.motor_parts_exchanges == valid_data["motor_parts_exchanges"]


@pytest.mark.parametrize(
    "pit_number,tilt,is_new_propeller,motor_parts_exchanges,expected",
    [
        (7, 2.5, True, [], False),  # invalid pit_number
        (3, -0.6, True, [], False),  # invalid tilt (below lower limit)
        (3, 3.1, True, [], False),  # invalid tilt (above upper limit)
    ],
)
def test_boat_setting_invalid(pit_number, tilt, is_new_propeller, motor_parts_exchanges, expected):  # type: ignore
    data = {
        **base_data,
        "pit_number": pit_number,
        "tilt": tilt,
        "is_new_propeller": is_new_propeller,
        "motor_parts_exchanges": motor_parts_exchanges,
    }
    if expected:
        BoatSetting(**data)
    else:
        with pytest.raises(ValidationError):
            BoatSetting(**data)
        with pytest.raises(ValidationError):
            BoatSetting(**data)


@pytest.mark.parametrize(
    "pit_number,start_course,start_time,expected",
    [
        # valid case
        (1, 1, 1.23, True),
        # invalid cases
        (1, 0, 1.23, False),  # invalid start_course
        (1, 7, 1.23, False),  # invalid start_course
        (1, 1, None, False),  # missing start_time
    ],
)
def test_start_exhibition_record(pit_number, start_course, start_time, expected):  # type: ignore
    data = {
        **base_data,
        "pit_number": pit_number,
        "start_course": start_course,
        "start_time": start_time,
    }
    if expected:
        record = StartExhibitionRecord(**data)
        assert record.pit_number == data["pit_number"]
        assert record.start_course == data["start_course"]
        assert record.start_time == data["start_time"]
    else:
        with pytest.raises(ValidationError):
            record = StartExhibitionRecord(**data)
            record = StartExhibitionRecord(**data)


@pytest.mark.parametrize(
    "pit_number,exhibition_time,expected",
    [
        # valid case
        (1, 1.23, True),
        # invalid cases
        (1, None, False),  # missing exhibition_time
    ],
)
def test_circumference_exhibition_record(pit_number, exhibition_time, expected):  # type: ignore
    data = {
        **base_data,
        "pit_number": pit_number,
        "exhibition_time": exhibition_time,
    }
    if expected:
        record = CircumferenceExhibitionRecord(**data)
        assert record.pit_number == data["pit_number"]
        assert record.exhibition_time == data["exhibition_time"]
    else:
        with pytest.raises(ValidationError):
            record = CircumferenceExhibitionRecord(**data)
        with pytest.raises(ValidationError):
            record = CircumferenceExhibitionRecord(**data)


@pytest.mark.parametrize(
    "pit_number,start_course,arrival,total_time,start_time,winning_trick,disqualification,expected",
    [
        # valid cases
        (1, 1, 1, 1.23, 1.23, WinningTrick.NIGE, None, True),
        (1, 1, 1, None, None, WinningTrick.NIGE, None, True),  # missing total_time and start_time
        # invalid cases
        (1, 0, 1, 1.23, 1.23, WinningTrick.NIGE, None, False),  # invalid start_course
        (1, 7, 1, 1.23, 1.23, WinningTrick.NIGE, None, False),  # invalid start_course
        (1, 1, 0, 1.23, 1.23, WinningTrick.NIGE, None, False),  # invalid arrival
        (1, 1, 7, 1.23, 1.23, WinningTrick.NIGE, None, False),  # invalid arrival
    ],
)
def test_race_record(  # type: ignore
    pit_number,
    start_course,
    arrival,
    total_time,
    start_time,
    winning_trick,
    disqualification,
    expected,
):
    data = {
        **base_data,
        "pit_number": pit_number,
        "start_course": start_course,
        "arrival": arrival,
        "total_time": total_time,
        "start_time": start_time,
        "winning_trick": winning_trick,
        "disqualification": disqualification,
    }
    if expected:
        record = RaceRecord(**data)
        assert record.pit_number == data["pit_number"]
        assert record.start_course == data["start_course"]
        assert record.arrival == data["arrival"]
        assert record.total_time == data["total_time"]
        assert record.start_time == data["start_time"]
        assert record.winning_trick == data["winning_trick"]
        assert record.disqualification == data["disqualification"]
    else:
        with pytest.raises(ValidationError):
            record = RaceRecord(**data)
