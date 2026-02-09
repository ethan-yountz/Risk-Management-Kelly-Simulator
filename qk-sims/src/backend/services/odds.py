import math
from collections import Counter


def implied_prob(odds: float):
    if odds > 0:
        return 100 / (odds + 100)
    odds = abs(odds)
    return odds / (odds + 100)


def multiplicative_devig(odds1: float, odds2: float):
    total_implied_prob = implied_prob(odds1) + implied_prob(odds2)
    return implied_prob(odds1) / total_implied_prob


def additive_devig(odds1: float, odds2: float):
    q1 = implied_prob(odds1)
    q2 = implied_prob(odds2)
    overround = (q1 + q2) - 1
    k = overround / 2
    return q1 - k


def power_devig(odds1: float, odds2: float):
    q1 = implied_prob(odds1)
    q2 = implied_prob(odds2)
    alpha = 1.0

    for _ in range(20):
        q1_alpha = q1**alpha
        q2_alpha = q2**alpha
        sum_powered = q1_alpha + q2_alpha
        error = sum_powered - 1

        if abs(error) < 1e-8:
            break

        derivative = q1_alpha * math.log(q1) + q2_alpha * math.log(q2)
        if abs(derivative) < 1e-10:
            break

        alpha = max(alpha - (error / derivative), 0.01)

    q1_powered = q1**alpha
    q2_powered = q2**alpha
    total_powered = q1_powered + q2_powered
    return q1_powered / total_powered


def worst_case_devig(odds1: float, odds2: float):
    methods = {
        "multiplicative": multiplicative_devig(odds1, odds2),
        "additive": additive_devig(odds1, odds2),
        "power": power_devig(odds1, odds2),
    }
    min_method = min(methods.items(), key=lambda item: item[1])
    return min_method[1], min_method[0]


def prob_to_american_odds(prob: float):
    if prob > 0.5:
        return -int((prob / (1 - prob)) * 100)
    return int(((1 - prob) / prob) * 100)


def calculate_market_juice(original_prob: float, fair_prob: float):
    return ((original_prob - fair_prob) / original_prob) * 100


def calculate_kelly_wager(
    fair_prob: float,
    payout_odds: float,
    bankroll: float,
    kelly_fraction: float,
):
    payout_prob = implied_prob(payout_odds)
    edge = ((fair_prob - payout_prob) / payout_prob) * 100

    if payout_odds > 0:
        b = payout_odds / 100
    else:
        b = 100 / abs(payout_odds)

    p = fair_prob
    q = 1 - fair_prob
    kelly_percentage = (b * p - q) / b
    kelly_wager = bankroll * kelly_fraction * kelly_percentage

    return {
        "edge_percent": edge,
        "kelly_percentage": kelly_percentage * 100,
        "kelly_wager": kelly_wager,
        "full_kelly": 100 * kelly_percentage,
        "half_kelly": (100 * kelly_percentage) / 2,
        "quarter_kelly": (100 * kelly_percentage) / 4,
        "is_profitable": kelly_percentage > 0,
    }


def most_common_method(methods):
    method_counts = Counter(methods)
    return method_counts.most_common(1)[0][0]
