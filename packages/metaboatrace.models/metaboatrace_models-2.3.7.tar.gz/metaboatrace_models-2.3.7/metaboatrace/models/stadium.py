from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, StrictInt, model_validator
from typing_extensions import Self


class StadiumTelCode(Enum):
    KIRYU = 1
    TODA = 2
    EDOGAWA = 3
    HEIWAJIMA = 4
    TAMAGAWA = 5
    HAMANAKO = 6
    GAMAGORI = 7
    TOKONAME = 8
    TSU = 9
    MIKUNI = 10
    BIWAKO = 11
    SUMINOE = 12
    AMAGASAKI = 13
    NARUTO = 14
    MARUGAME = 15
    KOJIMA = 16
    MIYAJIMA = 17
    TOKUYAMA = 18
    SHIMONOSEKI = 19
    WAKAMATSU = 20
    ASHIYA = 21
    FUKUOKA = 22
    KARATSU = 23
    OMURA = 24


class SeriesGrade(Enum):
    SG = 1
    G1 = 2
    G2 = 3
    G3 = 4
    NO_GRADE = 5

    @classmethod
    def from_string(cls, s: str) -> "SeriesGrade":
        return cls.__members__[s]


class SeriesKind(Enum):
    UNCATEGORIZED = 1
    ALL_LADIES = 2
    VENUS = 3
    ROOKIE = 4
    SENIOR = 5
    DOUBLE_WINNER = 6
    TOURNAMENT = 7


class Event(BaseModel):
    stadium_tel_code: StadiumTelCode
    starts_on: date
    # note: 開催自体は最長7日だが、過去のデータをクロールする場合は順延した日数も加算される
    # 例えば以下
    # https://boatrace.jp/owpc/pc/race/raceindex?jcd=09&hd=20230513
    # 開催の最長7日と順延の最長2日を考慮して最大値は9日にする
    days: StrictInt = Field(..., ge=3, le=9)
    grade: SeriesGrade
    kind: SeriesKind
    title: str


class MotorRenewal(BaseModel):
    stadium_tel_code: StadiumTelCode
    date: date


class EventHoldingStatus(Enum):
    OPEN = "open"
    CANCELED = "canceled"
    POSTPONED = "postponed"


class EventHolding(BaseModel):
    stadium_tel_code: StadiumTelCode
    date: Optional[date]
    status: EventHoldingStatus
    progress_day: Optional[int] = None  # HACK: 最終日は-1で表現

    @model_validator(mode="after")
    def validate_status_and_progress_day(self) -> Self:
        if self.status == EventHoldingStatus.OPEN:
            if self.progress_day is None:
                raise ValueError("progress_day is required when status is OPEN")
            if self.progress_day not in [-1, 1, 2, 3, 4, 5, 6, 7]:
                raise ValueError("progress_day must be one of -1, 1, 2, 3, 4, 5, 6, 7")
        else:
            if self.progress_day is not None:
                raise ValueError("progress_day must be None when status is not OPEN")
        return self
