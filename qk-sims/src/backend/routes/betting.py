from fastapi import APIRouter

from services.betting import generate_complete_output, input_to_odds, parse_odds_string

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Hello, world!"}


@router.get("/square/{x}")
def square(x: int):
    return {"input": x, "output": x * x}


@router.get("/parse-odds/{odds_str}")
def parse_odds(odds_str: str):
    result = parse_odds_string(odds_str)
    if result is None:
        return {"error": "Invalid odds format", "input": odds_str}
    result["input"] = odds_str
    return result


@router.get("/calculate-bet")
def calculate_bet(
    input_str: str,
    final_odds: int,
    bankroll: float,
    kelly_fraction: float,
    devig_method: str = "worst_case",
):
    try:
        parsed_legs = input_to_odds(input_str)
        output = generate_complete_output(
            parsed_legs,
            final_odds,
            bankroll,
            kelly_fraction,
            devig_method,
        )
        return {"output": output, "parsed_legs": parsed_legs}
    except Exception as exc:
        return {"error": str(exc), "input": input_str}
