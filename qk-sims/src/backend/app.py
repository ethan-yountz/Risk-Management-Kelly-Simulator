from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.betting import router as betting_router
from routes.simulation import router as simulation_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(betting_router)
    app.include_router(simulation_router)
    return app


app = create_app()
