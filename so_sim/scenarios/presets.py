"""Preloaded scenarios (one-click demos) for SmartLabOS."""
from ..core.config import MundoConfig


# --- 1) Basic mix of processes ------------------
BASICO = {
    "descripcion": "Basic: 4 processes to demonstrate scheduling and memory allocation.",
    "scheduler": "fcfs", "quantum": 3,
    "ram_total": 4096, "ram_so": 512, "tam_bloque": 256,
    "estrategia_mem": "first_fit",
    "paginacion_activa": False,
    "procesos": [
        {"pid": 1, "nombre": "Process A", "llegada": 0, "rafaga": 5, "prioridad": 2, "tam_proceso": 512},
        {"pid": 2, "nombre": "Process B", "llegada": 1, "rafaga": 3, "prioridad": 1, "tam_proceso": 256},
        {"pid": 3, "nombre": "Process C", "llegada": 2, "rafaga": 4, "prioridad": 3, "tam_proceso": 512},
        {"pid": 4, "nombre": "Process D", "llegada": 3, "rafaga": 2, "prioridad": 2, "tam_proceso": 256},
    ],
}

# --- 2) Round Robin with quantum ----------------------------------------------
ROUND_ROBIN = {
    "descripcion": "Round Robin with quantum=2: observe time-sharing in Gantt chart.",
    "scheduler": "rr", "quantum": 2,
    "ram_total": 4096, "ram_so": 512, "tam_bloque": 256,
    "estrategia_mem": "first_fit",
    "paginacion_activa": False,
    "procesos": [
        {"pid": 1, "nombre": "Task1", "llegada": 0, "rafaga": 5, "prioridad": 1, "tam_proceso": 256},
        {"pid": 2, "nombre": "Task2", "llegada": 0, "rafaga": 4, "prioridad": 1, "tam_proceso": 256},
        {"pid": 3, "nombre": "Task3", "llegada": 1, "rafaga": 6, "prioridad": 1, "tam_proceso": 512},
    ],
}

# --- 3) Priority scheduling ----------------------------------
PRIORITY_DEMO = {
    "descripcion": "Priority (non-preemptive): lower number = higher priority.",
    "scheduler": "prioridad_np", "quantum": 3,
    "ram_total": 4096, "ram_so": 512, "tam_bloque": 256,
    "estrategia_mem": "best_fit",
    "paginacion_activa": False,
    "procesos": [
        {"pid": 1, "nombre": "Low", "llegada": 0, "rafaga": 4, "prioridad": 3, "tam_proceso": 256},
        {"pid": 2, "nombre": "High", "llegada": 1, "rafaga": 3, "prioridad": 1, "tam_proceso": 256},
        {"pid": 3, "nombre": "Medium", "llegada": 2, "rafaga": 5, "prioridad": 2, "tam_proceso": 512},
    ],
}

# --- 4) CPU / I/O overlap (optional extension) ----------------------------------
IO_OVERLAP = {
    "descripcion": "CPU/I/O overlap: P1 blocks on I/O and CPU works on P2 (DMA model).",
    "scheduler": "fcfs", "quantum": 3,
    "ram_total": 4096, "ram_so": 512, "tam_bloque": 256,
    "estrategia_mem": "first_fit",
    "paginacion_activa": False,
    "procesos": [
        {"pid": 1, "nombre": "ReadDisk", "llegada": 0, "rafaga": 6, "prioridad": 1, "tam_proceso": 512,
         "io": [{"en_cpu": 2, "dispositivo": "Disk", "duracion": 4}]},
        {"pid": 2, "nombre": "Compute", "llegada": 1, "rafaga": 4, "prioridad": 1, "tam_proceso": 256},
    ],
}

PRESETS = {
    "basico": BASICO,
    "round_robin": ROUND_ROBIN,
    "priority": PRIORITY_DEMO,
    "io_overlap": IO_OVERLAP,
}

PRESET_DEFECTO = "basico"


# --- Demo workload (to evaluate/compare algorithms and strategies) -----
# A reproducible workload to demonstrate all 4 schedulers and memory strategies.
def _demo_workload_dict() -> dict:
    return {
        "descripcion": ("Demo workload: 8 processes to compare schedulers and memory strategies."),
        "scheduler": "fcfs", "quantum": 3, "costo_cambio": 1,
        "estrategia_mem": "first_fit",
        "ram_total": 4096, "ram_so": 512, "tam_bloque": 256,
        "paginacion_activa": False,
        "procesos": [
            {"pid": 1, "nombre": "P1", "llegada": 0, "rafaga": 8, "prioridad": 3, "tam_proceso": 512},
            {"pid": 2, "nombre": "P2", "llegada": 1, "rafaga": 4, "prioridad": 1, "tam_proceso": 256},
            {"pid": 3, "nombre": "P3", "llegada": 2, "rafaga": 9, "prioridad": 2, "tam_proceso": 768},
            {"pid": 4, "nombre": "P4", "llegada": 3, "rafaga": 5, "prioridad": 2, "tam_proceso": 256},
            {"pid": 5, "nombre": "P5", "llegada": 4, "rafaga": 2, "prioridad": 4, "tam_proceso": 512},
            {"pid": 6, "nombre": "P6", "llegada": 5, "rafaga": 6, "prioridad": 1, "tam_proceso": 256},
            {"pid": 7, "nombre": "P7", "llegada": 6, "rafaga": 3, "prioridad": 3, "tam_proceso": 512},
            {"pid": 8, "nombre": "P8", "llegada": 7, "rafaga": 7, "prioridad": 2, "tam_proceso": 256},
        ],
    }


def listar() -> list:
    items = [{"nombre": k, "descripcion": v["descripcion"]} for k, v in PRESETS.items()]
    items.append({"nombre": "demo_workload", "descripcion": _demo_workload_dict()["descripcion"]})
    return items


def cargar(nombre: str) -> MundoConfig:
    if nombre == "demo_workload":
        return MundoConfig.from_dict(_demo_workload_dict())
    if nombre not in PRESETS:
        raise KeyError(f"Unknown preset: {nombre}")
    return MundoConfig.from_dict(PRESETS[nombre])


def demo_workload() -> MundoConfig:
    return MundoConfig.from_dict(_demo_workload_dict())


def config_por_defecto() -> MundoConfig:
    return cargar(PRESET_DEFECTO)
