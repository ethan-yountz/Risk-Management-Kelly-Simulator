from typing import Dict, List, Optional

from pydantic import BaseModel


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
    confidenceIntervals: Dict[str, Dict[str, float]]
    simulations: List[float]
    simulationProgressions: List[List[float]]
    individualLegRecords: Optional[dict] = None
    parlayRecords: Optional[dict] = None
