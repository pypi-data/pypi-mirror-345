from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, StrictInt

from .region import Branch, Prefecture


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class RacerRank(Enum):
    A1 = 1
    A2 = 2
    B1 = 3
    B2 = 4

    @classmethod
    def from_string(cls, s: str) -> "RacerRank":
        return cls.__members__[s]


class Racer(BaseModel):
    registration_number: StrictInt
    last_name: str
    first_name: str = ""
    gender: Optional[Gender] = None
    term: Optional[StrictInt] = None
    birth_date: Optional[date] = None
    height: Optional[StrictInt] = None
    born_prefecture: Optional[Prefecture] = None
    branch: Optional[Branch] = None
    current_rating: Optional[RacerRank] = None


class RacerCondition(BaseModel):
    recorded_on: date
    racer_registration_number: StrictInt
    weight: float
    adjust: float


class RacerPerformance(BaseModel):
    racer_registration_number: StrictInt
    aggregated_on: date
    rate_in_all_stadium: float
    rate_in_event_going_stadium: float


class EvaluationPeriodType(Enum):
    FIRST_HALF = 1
    SECOND_HALF = 2


class RacerRatingEvaluationTerm:
    FIRST_HALF_START_MONTH = 5
    SECOND_HALF_START_MONTH = 11

    def __init__(self, year: int, period_type: EvaluationPeriodType):
        self.year = year
        self.period_type = period_type
        self.starts_on, self.ends_on = self._calculate_term_dates()

    def _calculate_term_dates(self) -> tuple[date, date]:
        if self.period_type == EvaluationPeriodType.FIRST_HALF:
            starts_on = date(self.year, self.FIRST_HALF_START_MONTH, 1)
            ends_on = date(self.year, self.SECOND_HALF_START_MONTH - 1, 31)
        else:
            starts_on = date(self.year, self.SECOND_HALF_START_MONTH, 1)
            ends_on = date(self.year + 1, self.FIRST_HALF_START_MONTH - 1, 30)
        return starts_on, ends_on

    def prev(self) -> "RacerRatingEvaluationTerm":
        if self.period_type == EvaluationPeriodType.FIRST_HALF:
            return RacerRatingEvaluationTerm(self.year - 1, EvaluationPeriodType.SECOND_HALF)
        else:
            return RacerRatingEvaluationTerm(self.year, EvaluationPeriodType.FIRST_HALF)

    def next(self) -> "RacerRatingEvaluationTerm":
        if self.period_type == EvaluationPeriodType.FIRST_HALF:
            return RacerRatingEvaluationTerm(self.year, EvaluationPeriodType.SECOND_HALF)
        else:
            return RacerRatingEvaluationTerm(self.year + 1, EvaluationPeriodType.FIRST_HALF)
