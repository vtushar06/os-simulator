"""Centralized scheduling metrics calculation.

Time convention: tick `t` covers the interval [t, t+1). A process that
terminates during tick `t_fin` completes at `t_fin + 1`.
  - turnaround = (t_fin + 1) - arrival
  - response   = t_first_dispatch - arrival
  - wait       = ticks the process spent in READY state (wait_accumulated)
Wait is measured directly (not derived), so it's exact even with I/O
in between. Averages are computed only over TERMINATED processes normally
(those that abort with ERROR are counted separately).
"""
from typing import List, Optional

from .enums import Estado
from .pcb import PCB


def retorno(p: PCB) -> Optional[int]:
    if p.t_fin is None:
        return None
    return (p.t_fin + 1) - p.llegada


def respuesta(p: PCB) -> Optional[int]:
    if p.t_primer_despacho is None:
        return None
    return p.t_primer_despacho - p.llegada


def espera(p: PCB) -> int:
    return p.espera_acumulada


def metricas_proceso(p: PCB) -> dict:
    return {"espera": espera(p), "retorno": retorno(p), "respuesta": respuesta(p)}


def resumen_errores(procesos: List[PCB]) -> dict:
    ok = sum(1 for p in procesos if p.estado == Estado.TERMINADO)
    con_error = sum(1 for p in procesos if p.estado == Estado.ERROR)
    return {"terminados_ok": ok, "con_error": con_error}


def promedios(procesos: List[PCB]) -> dict:
    terminados = [p for p in procesos if p.estado == Estado.TERMINADO]
    err = resumen_errores(procesos)
    if not terminados:
        return {"espera": None, "retorno": None, "respuesta": None,
                "terminados": 0, "total": len(procesos),
                "terminados_ok": err["terminados_ok"], "con_error": err["con_error"]}
    n = len(terminados)
    prom_esp = sum(espera(p) for p in terminados) / n
    prom_ret = sum(retorno(p) for p in terminados) / n
    resp = [respuesta(p) for p in terminados if respuesta(p) is not None]
    prom_resp = sum(resp) / len(resp) if resp else None
    return {
        "espera": round(prom_esp, 2),
        "retorno": round(prom_ret, 2),
        "respuesta": round(prom_resp, 2) if prom_resp is not None else None,
        "terminados": n, "total": len(procesos),
        "terminados_ok": err["terminados_ok"], "con_error": err["con_error"],
    }
