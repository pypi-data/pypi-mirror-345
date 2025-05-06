from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, StrictInt, field_validator

from .boat import MotorParts
from .stadium import StadiumTelCode


class Weather(Enum):
    FINE = 1
    CLOUDY = 2
    RAINY = 3
    SNOWY = 4
    TYPHOON = 5
    FOG = 6


class BettingMethod(Enum):
    TRIFECTA = 1


class WinningTrick(Enum):
    NIGE = 1
    SASHI = 2
    MAKURI = 3
    MAKURIZASHI = 4
    NUKI = 5
    MEGUMARE = 6

    def valid_courses(self) -> set[int]:
        """Returns a set of valid course numbers (1-6) based on the winning trick."""
        if self == WinningTrick.NIGE:
            return {1}
        elif self in {WinningTrick.SASHI, WinningTrick.MAKURI}:
            return {2, 3, 4, 5, 6}
        elif self == WinningTrick.MAKURIZASHI:
            return {3, 4, 5, 6}
        else:
            return {1, 2, 3, 4, 5, 6}


class Disqualification(Enum):
    CAPSIZE = 1
    FALL = 2
    SINKING = 3
    VIOLATION = 4
    DISQUALIFICATION_AFTER_START = 5
    ENGINE_STOP = 6
    UNFINISHED = 7
    REPAYMENT_OTHER_THAN_FLYING_AND_LATENESS = 8
    FLYING = 9
    LATENESS = 10
    ABSENT = 11


class _RaceIdentifier(BaseModel):
    race_holding_date: date
    stadium_tel_code: StadiumTelCode
    race_number: StrictInt = Field(..., ge=1, le=12)


class _RaceEntryIdentifier(_RaceIdentifier):
    pit_number: StrictInt = Field(..., ge=1, le=6)


class _BettingMixin(BaseModel):
    betting_method: BettingMethod = BettingMethod.TRIFECTA
    betting_numbers: list[int]

    @field_validator("betting_numbers")
    def validate_betting_numbers(cls, betting_numbers: list[int]) -> list[int]:
        if len(betting_numbers) > 3:
            raise ValueError("Betting numbers should have at most 3 elements")
        for betting_number in betting_numbers:
            if betting_number < 1 or betting_number > 6:
                raise ValueError("Each betting number must be between 1 and 6")
        return betting_numbers


class RaceInformation(_RaceIdentifier):
    title: str
    number_of_laps: Literal[2, 3]
    deadline_at: datetime
    is_course_fixed: bool
    use_stabilizer: bool


class WeatherCondition(_RaceIdentifier):
    in_performance: bool
    weather: Weather
    wavelength: Optional[float]
    wind_angle: Optional[float] = Field(None, ge=0, le=360)
    wind_velocity: float
    air_temperature: float
    water_temperature: float


class RaceEntry(_RaceEntryIdentifier):
    racer_registration_number: StrictInt
    is_absent: bool
    motor_number: StrictInt = Field(..., ge=1, le=99)
    boat_number: StrictInt = Field(..., ge=1, le=999)


class StartExhibitionRecord(_RaceEntryIdentifier):
    start_course: StrictInt = Field(..., ge=1, le=6)
    start_time: float


class CircumferenceExhibitionRecord(_RaceEntryIdentifier):
    exhibition_time: float


class BoatSetting(_RaceEntryIdentifier):
    boat_number: Optional[int] = None
    motor_number: Optional[int] = None
    tilt: Optional[float] = Field(None, ge=-0.5, le=3.0)
    is_new_propeller: Optional[bool] = None
    motor_parts_exchanges: list[tuple[MotorParts, StrictInt]]


class Odds(_RaceIdentifier, _BettingMixin):
    ratio: Optional[float] = Field(None, ge=0, le=9999.0)


class Payoff(_RaceIdentifier, _BettingMixin):
    amount: StrictInt = Field(..., ge=100)


class RaceRecord(_RaceEntryIdentifier):
    start_course: Optional[StrictInt] = Field(None, ge=1, le=6)
    arrival: Optional[StrictInt] = Field(None, ge=1, le=6)
    total_time: Optional[float] = None
    start_time: Optional[float] = None
    winning_trick: Optional[WinningTrick] = None
    disqualification: Optional[Disqualification] = None
