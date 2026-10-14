"""SmartLabOS: FastAPI layer that serves the UI and routes commands to the core.
All OS logic lives in `so_sim.core` (pure Python)."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import routes_config, routes_control, routes_state
from .manager import SimulationManager
from .scenarios import presets

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # SimulationManager is created when the loop is already running.
    app.state.manager = SimulationManager(presets.config_por_defecto())
    yield
    await app.state.manager.shutdown()


app = FastAPI(title="SmartLabOS", version="1.0.0", lifespan=lifespan)

app.include_router(routes_control.router)
app.include_router(routes_state.router)
app.include_router(routes_config.router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
