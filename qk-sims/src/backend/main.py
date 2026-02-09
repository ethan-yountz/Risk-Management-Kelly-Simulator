from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import math
import random
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,  
    allow_methods=["*"],
    allow_headers=["*"],
)

def implied_prob(odds: float):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        odds = abs(odds)
        return odds / (odds + 100)

def multiplicative_devig(odds1: float, odds2: float):
    
    total_implied_prob = implied_prob(odds1) + implied_prob(odds2)
    return implied_prob(odds1) / total_implied_prob

def additive_devig(odds1: float, odds2: float):
    
    q1 = implied_prob(odds1)
    q2 = implied_prob(odds2)
    S = q1 + q2
    overround = S - 1
    
    k = overround / 2
    
    p1 = q1 - k
    p2 = q2 - k
    
    return p1

def power_devig(odds1: float, odds2: float):
    import math
    
    q1 = implied_prob(odds1)
    q2 = implied_prob(odds2)
    
    S = q1 + q2
    overround = S - 1
    
    
    alpha = 1.0
    
    for _ in range(20):
        q1_alpha = q1 ** alpha
        q2_alpha = q2 ** alpha
        sum_powered = q1_alpha + q2_alpha
        
        error = sum_powered - 1
        
        if abs(error) < 1e-8:
            break
            
        derivative = q1_alpha * math.log(q1) + q2_alpha * math.log(q2)
        
        if abs(derivative) < 1e-10:
            break
            
        alpha = alpha - error / derivative
        
        alpha = max(alpha, 0.01)
    
    q1_powered = q1 ** alpha
    q2_powered = q2 ** alpha
    
    total_powered = q1_powered + q2_powered
    p1 = q1_powered / total_powered
    
    return p1

def worst_case_devig(odds1: float, odds2: float):
    methods = {
        "multiplicative": multiplicative_devig(odds1, odds2),
        "additive": additive_devig(odds1, odds2),
        "power": power_devig(odds1, odds2)
    }
    

    min_method = min(methods.items(), key=lambda x: x[1])
    
    return min_method[1], min_method[0]

def prob_to_american_odds(prob):
    if prob > 0.5:
        return -int((prob / (1 - prob)) * 100)
    else:
        return int(((1 - prob) / prob) * 100)

def calculate_market_juice(original_prob, fair_prob):
    return (original_prob - fair_prob) / original_prob * 100

def calculate_kelly_wager(fair_prob, payout_odds, bankroll, kelly_fraction):
    payout_prob = implied_prob(payout_odds)
    
    edge = (fair_prob - payout_prob) / payout_prob * 100
    
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
        "half_kelly": 100 * kelly_percentage / 2,
        "quarter_kelly": 100 * kelly_percentage / 4,
        "is_profitable": kelly_percentage > 0
    }

def seperate_odd_list(input_str: str):
    parts = [part.strip() for part in input_str.split(",")]
    return parts

def parse_odds_string(odds_str: str):
    if "/" in odds_str:
        parts = odds_str.split("/")
        if len(parts) == 2:
            try:
                odds1 = float(parts[0].strip())
                odds2 = float(parts[1].strip())
                return {"type": "odds", "odds1": odds1, "odds2": odds2}
            except ValueError:
                return None
        else:
            return None
    else:
        try:
            num = float(odds_str.strip())
            return {"type": "probability", "value": num}
        except ValueError:
            return None

def input_to_odds(input_str: str):
    parts = seperate_odd_list(input_str)
    parsed_legs = []
    for part in parts:
        odds = parse_odds_string(part)
        parsed_legs.append(odds)
    return parsed_legs

def generate_leg_output(leg, leg_number):
    if leg is None:
        raise ValueError(f"Invalid leg data for leg {leg_number}")
    
    if leg["type"] == "odds":
        fair_value = multiplicative_devig(leg["odds1"], leg["odds2"])
        
        original_prob = implied_prob(leg["odds1"])
        market_juice = calculate_market_juice(original_prob, fair_value)
        
        fair_odds = prob_to_american_odds(fair_value)
        fair_percent = fair_value * 100
        
        return f"Leg#{leg_number} ({leg['odds1']}); Market Juice = {market_juice:.1f}%; Fair Value = {fair_odds:+} ({fair_percent:.1f}%)"
    
    else:  
        fair_value = leg["value"] / 100
        fair_odds = prob_to_american_odds(fair_value)
        fair_percent = fair_value * 100
        
        return f"Leg#{leg_number} ({leg['value']}%); Fair Value = {fair_odds:+} ({fair_percent:.1f}%)"

def generate_complete_output(parsed_legs, final_odds, bankroll, kelly_fraction, devig_method="worst_case"):
    output = []
    actual_method_used = devig_method  
    
    for i, leg in enumerate(parsed_legs):
        leg_output = generate_leg_output(leg, i + 1)
        output.append(leg_output)
    
    total_fv = 1
    worst_case_methods = []  
    
    for i, leg in enumerate(parsed_legs):
        if leg["type"] == "odds":
            if devig_method == "multiplicative":
                fair_value = multiplicative_devig(leg["odds1"], leg["odds2"])
            elif devig_method == "additive":
                fair_value = additive_devig(leg["odds1"], leg["odds2"])
            elif devig_method == "power":
                fair_value = power_devig(leg["odds1"], leg["odds2"])
            elif devig_method == "worst_case":
                fair_value, method_used = worst_case_devig(leg["odds1"], leg["odds2"])
                worst_case_methods.append(method_used)
            else:  
                fair_value = multiplicative_devig(leg["odds1"], leg["odds2"])
        else:
            fair_value = leg["value"] / 100
        total_fv *= fair_value
    
    if devig_method == "worst_case" and worst_case_methods:
        from collections import Counter
        method_counts = Counter(worst_case_methods)
        actual_method_used = method_counts.most_common(1)[0][0]

    kelly_data = calculate_kelly_wager(total_fv, final_odds, bankroll, kelly_fraction)
    
    if devig_method == "worst_case":
        method_display = {
            "multiplicative": "Worst-case (Multiplicative)",
            "additive": "Worst-case (Additive)", 
            "power": "Worst-case (Power)"
        }.get(actual_method_used, "Worst-case")
    else:
        method_display = {
            "multiplicative": "Multiplicative",
            "additive": "Additive",
            "power": "Power"
        }.get(devig_method, "Worst-case")
    
    output.insert(0, f"{method_display}")
    output.append(f"Final Odds: {final_odds}; Fair Value = {prob_to_american_odds(total_fv)} ({total_fv * 100:.1f}%)")
    
    if kelly_data['is_profitable']:
        output.append(f"Summary: EV% = {kelly_data['edge_percent']:.1f}%, Kelly Wager = ${kelly_data['kelly_wager']:.2f} (Full={kelly_data['full_kelly']:.2f}u, 1/2={kelly_data['half_kelly']:.2f}u, 1/4={kelly_data['quarter_kelly']:.2f}u)")
    else:
        output.append(f"Summary: EV% = {kelly_data['edge_percent']:.1f}% - No profitable Kelly wager (negative edge)")
    
    return output


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.get("/square/{x}")
def square(x: int):
    return {"input": x, "output": x * x}

@app.get("/parse-odds/{odds_str}")
def parse_odds(odds_str: str):
    result = parse_odds_string(odds_str)
    if result is None:
        return {"error": "Invalid odds format", "input": odds_str}
    
    result["input"] = odds_str
    return result

@app.get("/calculate-bet")
def calculate_bet(input_str: str, final_odds: int, bankroll: float, kelly_fraction: float, devig_method: str = "worst_case"):
    """Calculate the complete betting analysis"""
    try:
        parsed_legs = input_to_odds(input_str)
        output = generate_complete_output(parsed_legs, final_odds, bankroll, kelly_fraction, devig_method)
        return {"output": output, "parsed_legs": parsed_legs}
    except Exception as e:
        return {"error": str(e), "input": input_str}


class Leg(BaseModel):
    id: int
    fairProbability: Optional[float] = None
    payoutOdds: float
    edgePercent: Optional[float] = None

class MonteCarloRequest(BaseModel):
    starting_bankroll: float
    kelly_fraction: float
    sample_size: int
    legs: List[Leg]
    mode: str
    fair_prob_one_leg: Optional[float] = None
    total_payout: Optional[float] = None
    number_of_legs: Optional[int] = None
    estimated_edge: Optional[float] = None
    payout_per_bet: Optional[float] = None
    num_simulations: int = 1000

class SimulationResults(BaseModel):
    probabilityOfProfit: float
    meanFinalBankroll: float
    medianFinalBankroll: float
    riskOfRuin: float
    confidenceIntervals: dict
    simulations: List[float]
    simulationProgressions: List[List[float]]
    individualLegRecords: Optional[dict] = None
    parlayRecords: Optional[dict] = None

def run_monte_carlo_simulation(request: MonteCarloRequest) -> SimulationResults:
    final_bankrolls = []
    individual_leg_wins = {}
    parlay_wins = []
    simulation_progressions = []
    
    random.seed(42)
    np.random.seed(42)
    
    for sim in range(request.num_simulations):
        current_bankroll = request.starting_bankroll
        leg_wins = {}
        bankroll_progression = [current_bankroll]
        if request.mode == "B" and request.legs:
            leg_wins = {leg.id: 0 for leg in request.legs}
        parlay_wins_sim = 0
        
        for bet in range(request.sample_size):
            if current_bankroll <= 0:
                break
                
            if request.mode == "A":
                fair_prob_one_leg = request.fair_prob_one_leg / 100
                total_payout = request.total_payout
                num_legs = request.number_of_legs
                
                combined_fair_prob = fair_prob_one_leg ** num_legs
                
                if total_payout < 0:
                    implied_prob_value = abs(total_payout) / (abs(total_payout) + 100)
                else:
                    implied_prob_value = implied_prob(total_payout)
                edge = combined_fair_prob - implied_prob_value
                
                if edge >= 0:
                    kelly_percentage = edge / implied_prob_value if implied_prob_value > 0 else 0
                    wager = request.starting_bankroll * request.kelly_fraction * kelly_percentage
                else:
                    wager = request.starting_bankroll * 0.01
                
                parlay_wins_current_bet = True
                for leg in range(num_legs):
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
                    kelly_percentage = edge / implied_prob_value if implied_prob_value > 0 else 0
                    wager = request.starting_bankroll * request.kelly_fraction * kelly_percentage
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
            "roi": float((bottom1_value - request.starting_bankroll) / request.starting_bankroll * 100)
        },
        "bottom5": {
            "value": bottom5_value,
            "roi": float((bottom5_value - request.starting_bankroll) / request.starting_bankroll * 100)
        },
        "bottom10": {
            "value": bottom10_value,
            "roi": float((bottom10_value - request.starting_bankroll) / request.starting_bankroll * 100)
        },
        "top10": {
            "value": top10_value,
            "roi": float((top10_value - request.starting_bankroll) / request.starting_bankroll * 100)
        },
        "top5": {
            "value": top5_value,
            "roi": float((top5_value - request.starting_bankroll) / request.starting_bankroll * 100)
        },
        "top1": {
            "value": top1_value,
            "roi": float((top1_value - request.starting_bankroll) / request.starting_bankroll * 100)
        }
    }
    
    betting_records = {
        "total_wins": int(np.sum(parlay_wins)),
        "total_bets": int(len(parlay_wins) * request.sample_size),
        "win_rate": float(np.mean(parlay_wins)) if parlay_wins else 0.0
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
        parlayRecords=betting_records
    )

@app.post("/monte-carlo-simulation")
def monte_carlo_simulation(request: MonteCarloRequest):
    try:
        results = run_monte_carlo_simulation(request)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
