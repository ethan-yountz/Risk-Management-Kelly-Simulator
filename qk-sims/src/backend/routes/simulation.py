from fastapi import APIRouter

from schemas import MonteCarloRequest
from services.monte_carlo import run_monte_carlo_simulation

router = APIRouter()


@router.post("/monte-carlo-simulation")
def monte_carlo_simulation(request: MonteCarloRequest):
    try:
        results = run_monte_carlo_simulation(request)
        return {"results": results}
    except Exception as exc:
        return {"error": str(exc)}
