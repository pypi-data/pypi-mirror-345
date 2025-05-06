from datetime import date

import pytest
from pydantic import ValidationError

from metaboatrace.models.race import BettingMethod, Odds, Payoff, StadiumTelCode


@pytest.mark.parametrize(
    "betting_numbers, ratio, expected",
    [
        ([1, 2, 3], 1000.0, True),  # valid case
        ([1, 2, 3, 4], 1000.0, False),  # invalid betting_numbers
        ([1, 2, 3], 10000.0, False),  # invalid ratio
    ],
)
def test_odds(betting_numbers: list[int], ratio: float, expected: bool):  # type: ignore
    odds_data = {
        "race_holding_date": date.today(),
        "stadium_tel_code": StadiumTelCode.HEIWAJIMA,
        "race_number": 1,
        "betting_method": BettingMethod.TRIFECTA,
        "betting_numbers": betting_numbers,
        "ratio": ratio,
    }

    if expected:
        odds = Odds(**odds_data)  # type: ignore
        assert odds.race_holding_date == odds_data["race_holding_date"]
        assert odds.stadium_tel_code == odds_data["stadium_tel_code"]
        assert odds.race_number == odds_data["race_number"]
        assert odds.betting_method == odds_data["betting_method"]
        assert odds.betting_numbers == odds_data["betting_numbers"]
        assert odds.ratio == odds_data["ratio"]
    else:
        with pytest.raises(ValidationError):
            odds = Odds(**odds_data)  # type: ignore


@pytest.mark.parametrize(
    "race_holding_date,stadium_tel_code,race_number,betting_method,betting_numbers,amount,expected",
    [
        # valid cases
        (date.today(), StadiumTelCode.HEIWAJIMA, 1, BettingMethod.TRIFECTA, [1, 2, 3], 100, True),
        # invalid cases
        (
            date.today(),
            StadiumTelCode.HEIWAJIMA,
            1,
            BettingMethod.TRIFECTA,
            [1, 2, 3],
            90,
            False,
        ),  # invalid amount
        (
            date.today(),
            StadiumTelCode.HEIWAJIMA,
            1,
            BettingMethod.TRIFECTA,
            [1, 2, 3, 4],
            100,
            False,
        ),  # too many betting_numbers
        (
            date.today(),
            StadiumTelCode.HEIWAJIMA,
            1,
            BettingMethod.TRIFECTA,
            [1, 2, 7],
            100,
            False,
        ),  # invalid number in betting_numbers
    ],
)
def test_payoff(  # type: ignore
    race_holding_date,
    stadium_tel_code,
    race_number,
    betting_method,
    betting_numbers,
    amount,
    expected,
):
    data = {
        "race_holding_date": race_holding_date,
        "stadium_tel_code": stadium_tel_code,
        "race_number": race_number,
        "betting_method": betting_method,
        "betting_numbers": betting_numbers,
        "amount": amount,
    }
    if expected:
        payoff = Payoff(**data)
        assert payoff.race_holding_date == data["race_holding_date"]
        assert payoff.stadium_tel_code == data["stadium_tel_code"]
        assert payoff.race_number == data["race_number"]
        assert payoff.betting_method == data["betting_method"]
        assert payoff.betting_numbers == data["betting_numbers"]
        assert payoff.amount == data["amount"]
    else:
        with pytest.raises(ValidationError):
            payoff = Payoff(**data)
            payoff = Payoff(**data)
            payoff = Payoff(**data)
            payoff = Payoff(**data)
