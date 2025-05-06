from datetime import date

import pytest
from pydantic import ValidationError

from metaboatrace.models.boat import BoatPerformance, MotorPerformance, StadiumTelCode


@pytest.mark.parametrize(
    "quinella_rate,trio_rate,expected",
    [
        (50.0, 30.0, True),  # valid case
        (101.0, 30.0, False),  # invalid quinella_rate
        (50.0, 101.0, False),  # invalid trio_rate
    ],
)
def test_boat_performance(quinella_rate, trio_rate, expected):  # type: ignore
    boat_data = {
        "stadium_tel_code": StadiumTelCode.FUKUOKA,
        "recorded_date": date.today(),
        "number": 1,
        "quinella_rate": quinella_rate,
        "trio_rate": trio_rate,
    }

    if expected:
        boat = BoatPerformance(**boat_data)
        assert boat.stadium_tel_code == boat_data["stadium_tel_code"]
        assert boat.recorded_date == boat_data["recorded_date"]
        assert boat.number == boat_data["number"]
        assert boat.quinella_rate == boat_data["quinella_rate"]
        assert boat.trio_rate == boat_data["trio_rate"]
    else:
        with pytest.raises(ValidationError):
            boat = BoatPerformance(**boat_data)


@pytest.mark.parametrize(
    "quinella_rate, trio_rate, expected",
    [
        (50.0, 30.0, True),  # valid case
        (101.0, 30.0, False),  # invalid quinella_rate
        (50.0, 101.0, False),  # invalid trio_rate
    ],
)
def test_motor_performance(quinella_rate: float, trio_rate: float, expected: bool) -> None:
    motor_data = {
        "stadium_tel_code": StadiumTelCode.FUKUOKA,
        "recorded_date": date.today(),
        "number": 1,
        "quinella_rate": quinella_rate,
        "trio_rate": trio_rate,
    }

    if expected:
        motor = MotorPerformance(**motor_data)
        assert motor.stadium_tel_code == motor_data["stadium_tel_code"]
        assert motor.recorded_date == motor_data["recorded_date"]
        assert motor.number == motor_data["number"]
        assert motor.quinella_rate == motor_data["quinella_rate"]
        assert motor.trio_rate == motor_data["trio_rate"]
    else:
        with pytest.raises(ValidationError):
            motor = MotorPerformance(**motor_data)
