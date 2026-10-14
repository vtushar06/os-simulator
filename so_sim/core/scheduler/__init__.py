"""Scheduler factory for SmartLabOS."""
from typing import Optional

from ..enums import SchedAlgo
from .base import Scheduler
from .fcfs import FCFS
from .priority import Priority
from .round_robin import RoundRobin
from .sjf import SJF


def get_scheduler(nombre, quantum: Optional[int] = None) -> Scheduler:
    clave = nombre.value if isinstance(nombre, SchedAlgo) else str(nombre)
    if clave == SchedAlgo.FCFS.value:
        return FCFS()
    if clave == SchedAlgo.SJF.value:
        return SJF()
    if clave == SchedAlgo.RR.value:
        return RoundRobin(quantum=quantum or 3)
    if clave == SchedAlgo.PRIORIDAD_NP.value:
        return Priority(apropiativa=False)
    raise ValueError(f"Unknown scheduling algorithm: {nombre}")
