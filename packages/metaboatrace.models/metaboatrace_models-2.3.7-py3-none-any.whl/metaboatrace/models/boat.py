from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, StrictInt

from .stadium import StadiumTelCode


class MotorParts(Enum):
    ELECTRICAL_SYSTEM = 1
    CARBURETOR = 2
    PISTON = 3
    PISTON_RING = 4
    CYLINDER = 5
    CRANKSHAFT = 6
    GEAR_CASE = 7
    CARRIER_BODY = 8


class BoatPerformance(BaseModel):
    stadium_tel_code: StadiumTelCode
    recorded_date: date
    number: StrictInt = Field(..., ge=1, le=999)
    quinella_rate: Optional[float] = Field(None, ge=0, le=100)
    trio_rate: Optional[float] = Field(None, ge=0, le=100)


class MotorPerformance(BaseModel):
    stadium_tel_code: StadiumTelCode
    recorded_date: date
    number: StrictInt = Field(..., ge=1, le=99)
    quinella_rate: Optional[float] = Field(None, ge=0, le=100)
    trio_rate: Optional[float] = Field(None, ge=0, le=100)
