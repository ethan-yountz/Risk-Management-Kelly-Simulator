import random

import numpy as np

from schemas import MonteCarloRequest, SimulationResults
from services.odds import implied_prob


def run_monte_carlo_simulation(request: MonteCarloRequest) -> SimulationResults:
    final_bankrolls = []
    parlay_wins = []
    simulation_progressions = []

    random.seed(42)
    np.random.seed(42)

    for _ in range(request.num_simulations):
        current_bankroll = request.starting_bankroll
        bankroll_progression = [current_bankroll]
        parlay_wins_sim = 0

        for _ in range(request.sample_size):
            if current_bankroll <= 0:
                break

            if request.mode == "A":
                fair_prob_one_leg = request.fair_prob_one_leg / 100
                total_payout = request.total_payout
                num_legs = request.number_of_legs

                combined_fair_prob = fair_prob_one_leg**num_legs
                if total_payout < 0:
                    implied_prob_value = abs(total_payout) / (abs(total_payout) + 100)
                else:
                    implied_prob_value = implied_prob(total_payout)

                edge = combined_fair_prob - implied_prob_value
                if edge >= 0:
                    kelly_percentage = (
                        edge / implied_prob_value if implied_prob_value > 0 else 0
                    )
                    wager = (
                        request.starting_bankroll
                        * request.kelly_fraction
                        * kelly_percentage
                    )
                else:
                    wager = request.starting_bankroll * 0.01

                parlay_wins_current_bet = True
                for _ in range(num_legs):
                    if random.random() >= fair_prob_one_leg:
                        parlay_wins_current_bet = False
                        break

                if parlay_wins_current_bet:
                    if total_payout > 0:
                        current_bankroll += wager * (total_payout / 100)
                    else:
                        current_bankroll += wager * (100 / abs(total_payout))
                    parlay_wins_sim += 1
                else:
                    current_bankroll -= wager

                bankroll_progression.append(current_bankroll)

            elif request.mode == "B":
                edge_percent = request.estimated_edge / 100
                payout_odds = request.payout_per_bet
                implied_prob_value = implied_prob(payout_odds)
                fair_prob = implied_prob_value * (1 + edge_percent)
                edge = fair_prob - implied_prob_value

                if edge >= 0:
                    kelly_percentage = (
                        edge / implied_prob_value if implied_prob_value > 0 else 0
                    )
                    wager = (
                        request.starting_bankroll
                        * request.kelly_fraction
                        * kelly_percentage
                    )
                    wager = min(wager, request.starting_bankroll * 0.10)
                else:
                    wager = request.starting_bankroll * 0.01

                if random.random() < fair_prob:
                    current_bankroll += wager * (payout_odds / 100)
                else:
                    current_bankroll -= wager

                bankroll_progression.append(current_bankroll)

        final_bankrolls.append(current_bankroll)
        parlay_wins.append(parlay_wins_sim)
        simulation_progressions.append(bankroll_progression)

    final_bankrolls = np.array(final_bankrolls)
    prob_profit = np.mean(final_bankrolls > request.starting_bankroll)
    mean_final = np.mean(final_bankrolls)
    median_final = np.median(final_bankrolls)
    risk_of_ruin = np.mean(final_bankrolls <= 0)

    bottom1_value = float(np.percentile(final_bankrolls, 1))
    bottom5_value = float(np.percentile(final_bankrolls, 5))
    bottom10_value = float(np.percentile(final_bankrolls, 10))
    top10_value = float(np.percentile(final_bankrolls, 90))
    top5_value = float(np.percentile(final_bankrolls, 95))
    top1_value = float(np.percentile(final_bankrolls, 99))

    confidence_intervals = {
        "bottom1": {
            "value": bottom1_value,
            "roi": float(
                (bottom1_value - request.starting_bankroll)
                / request.starting_bankroll
                * 100
            ),
        },
        "bottom5": {
            "value": bottom5_value,
            "roi": float(
                (bottom5_value - request.starting_bankroll)
                / request.starting_bankroll
                * 100
            ),
        },
        "bottom10": {
            "value": bottom10_value,
            "roi": float(
                (bottom10_value - request.starting_bankroll)
                / request.starting_bankroll
                * 100
            ),
        },
        "top10": {
            "value": top10_value,
            "roi": float(
                (top10_value - request.starting_bankroll)
                / request.starting_bankroll
                * 100
            ),
        },
        "top5": {
            "value": top5_value,
            "roi": float(
                (top5_value - request.starting_bankroll)
                / request.starting_bankroll
                * 100
            ),
        },
        "top1": {
            "value": top1_value,
            "roi": float(
                (top1_value - request.starting_bankroll)
                / request.starting_bankroll
                * 100
            ),
        },
    }

    betting_records = {
        "total_wins": int(np.sum(parlay_wins)),
        "total_bets": int(len(parlay_wins) * request.sample_size),
        "win_rate": float(np.mean(parlay_wins)) if parlay_wins else 0.0,
    }

    return SimulationResults(
        probabilityOfProfit=float(prob_profit),
        meanFinalBankroll=float(mean_final),
        medianFinalBankroll=float(median_final),
        riskOfRuin=float(risk_of_ruin),
        confidenceIntervals=confidence_intervals,
        simulations=final_bankrolls.tolist(),
        simulationProgressions=simulation_progressions,
        individualLegRecords=None,
        parlayRecords=betting_records,
    )
