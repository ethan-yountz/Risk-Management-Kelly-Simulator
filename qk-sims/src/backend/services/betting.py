from services.odds import (
    additive_devig,
    calculate_kelly_wager,
    calculate_market_juice,
    implied_prob,
    most_common_method,
    multiplicative_devig,
    power_devig,
    prob_to_american_odds,
    worst_case_devig,
)


def separate_odd_list(input_str: str):
    return [part.strip() for part in input_str.split(",")]


def seperate_odd_list(input_str: str):
    return separate_odd_list(input_str)


def parse_odds_string(odds_str: str):
    if "/" in odds_str:
        parts = odds_str.split("/")
        if len(parts) != 2:
            return None
        try:
            odds1 = float(parts[0].strip())
            odds2 = float(parts[1].strip())
            return {"type": "odds", "odds1": odds1, "odds2": odds2}
        except ValueError:
            return None

    try:
        num = float(odds_str.strip())
        return {"type": "probability", "value": num}
    except ValueError:
        return None


def input_to_odds(input_str: str):
    return [parse_odds_string(part) for part in separate_odd_list(input_str)]


def generate_leg_output(leg, leg_number: int):
    if leg is None:
        raise ValueError(f"Invalid leg data for leg {leg_number}")

    if leg["type"] == "odds":
        fair_value = multiplicative_devig(leg["odds1"], leg["odds2"])
        original_prob = implied_prob(leg["odds1"])
        market_juice = calculate_market_juice(original_prob, fair_value)
        fair_odds = prob_to_american_odds(fair_value)
        fair_percent = fair_value * 100
        return (
            f"Leg#{leg_number} ({leg['odds1']}); Market Juice = {market_juice:.1f}%; "
            f"Fair Value = {fair_odds:+} ({fair_percent:.1f}%)"
        )

    fair_value = leg["value"] / 100
    fair_odds = prob_to_american_odds(fair_value)
    fair_percent = fair_value * 100
    return (
        f"Leg#{leg_number} ({leg['value']}%); Fair Value = "
        f"{fair_odds:+} ({fair_percent:.1f}%)"
    )


def _resolve_leg_fair_value(leg, devig_method: str, worst_case_methods):
    if leg["type"] != "odds":
        return leg["value"] / 100

    if devig_method == "multiplicative":
        return multiplicative_devig(leg["odds1"], leg["odds2"])
    if devig_method == "additive":
        return additive_devig(leg["odds1"], leg["odds2"])
    if devig_method == "power":
        return power_devig(leg["odds1"], leg["odds2"])
    if devig_method == "worst_case":
        fair_value, method_used = worst_case_devig(leg["odds1"], leg["odds2"])
        worst_case_methods.append(method_used)
        return fair_value
    return multiplicative_devig(leg["odds1"], leg["odds2"])


def _build_method_display(devig_method: str, actual_method_used: str):
    if devig_method == "worst_case":
        return {
            "multiplicative": "Worst-case (Multiplicative)",
            "additive": "Worst-case (Additive)",
            "power": "Worst-case (Power)",
        }.get(actual_method_used, "Worst-case")
    return {
        "multiplicative": "Multiplicative",
        "additive": "Additive",
        "power": "Power",
    }.get(devig_method, "Worst-case")


def generate_complete_output(
    parsed_legs,
    final_odds: int,
    bankroll: float,
    kelly_fraction: float,
    devig_method: str = "worst_case",
):
    output = [generate_leg_output(leg, i + 1) for i, leg in enumerate(parsed_legs)]
    total_fv = 1
    worst_case_methods = []
    actual_method_used = devig_method

    for leg in parsed_legs:
        total_fv *= _resolve_leg_fair_value(leg, devig_method, worst_case_methods)

    if devig_method == "worst_case" and worst_case_methods:
        actual_method_used = most_common_method(worst_case_methods)

    method_display = _build_method_display(devig_method, actual_method_used)
    kelly_data = calculate_kelly_wager(total_fv, final_odds, bankroll, kelly_fraction)

    output.insert(0, method_display)
    output.append(
        f"Final Odds: {final_odds}; Fair Value = {prob_to_american_odds(total_fv)} "
        f"({total_fv * 100:.1f}%)"
    )

    if kelly_data["is_profitable"]:
        output.append(
            f"Summary: EV% = {kelly_data['edge_percent']:.1f}%, Kelly Wager = "
            f"${kelly_data['kelly_wager']:.2f} (Full={kelly_data['full_kelly']:.2f}u, "
            f"1/2={kelly_data['half_kelly']:.2f}u, 1/4={kelly_data['quarter_kelly']:.2f}u)"
        )
    else:
        output.append(
            f"Summary: EV% = {kelly_data['edge_percent']:.1f}% - "
            "No profitable Kelly wager (negative edge)"
        )

    return output
