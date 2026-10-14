"""Preloaded scenarios (one-click demos) in English.

Each preset is a dict that `MundoConfig.from_dict` can read. Virtual addresses
use va = vpn << 12 (offset_bits=12), so VPN = va >> 12.
"""
from ..core.config import MundoConfig


def _va(vpn: int) -> int:
    return vpn << 12


# --- 1) Basic mix of processes with some memory and I/O ------------------
BASICO = {
    "descripcion": "Basic mix: 3 processes with memory accesses and I/O. Ideal to start.",
    "scheduler": "fcfs", "replacer": "fifo", "num_marcos": 4, "quantum": 3,
    "procesos": [
        {"pid": 1, "nombre": "Editor", "llegada": 0, "rafaga": 6, "prioridad": 2,
         "accesos": [{"en_cpu": 0, "va": _va(0)}, {"en_cpu": 1, "va": _va(1)},
                     {"en_cpu": 4, "va": _va(2)}],
         "io": [{"en_cpu": 3, "dispositivo": "Disk", "duracion": 3}]},
        {"pid": 2, "nombre": "Compiler", "llegada": 1, "rafaga": 4, "prioridad": 1,
         "accesos": [{"en_cpu": 0, "va": _va(0)}, {"en_cpu": 2, "va": _va(3)}]},
        {"pid": 3, "nombre": "Browser", "llegada": 2, "rafaga": 5, "prioridad": 3,
         "accesos": [{"en_cpu": 0, "va": _va(4)}, {"en_cpu": 1, "va": _va(1)}],
         "io": [{"en_cpu": 2, "dispositivo": "Printer", "duracion": 2}]},
    ],
}

# --- 2) Classic reference string to demonstrate page faults --------------
# Belady's classic string: 7 0 1 2 0 3 0 4 2 3 0 3 2 with 3 frames.
_CADENA = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
PAGE_FAULTS = {
    "descripcion": ("One process with classic reference string (7 0 1 2 0 3 0 4 2 3 0 3 2) "
                    "and only 3 frames. Change replacement algorithm and compare faults."),
    "scheduler": "fcfs", "replacer": "fifo", "num_marcos": 3, "quantum": 3,
    "procesos": [
        {"pid": 1, "nombre": "Demo-Pages", "llegada": 0, "rafaga": len(_CADENA),
         "accesos": [{"en_cpu": i, "va": _va(vpn)} for i, vpn in enumerate(_CADENA)]},
    ],
}

# --- 3) MLQ: two high (RR) and one low (FCFS) processes ------------------
MLQ_DEMO = {
    "descripcion": "MLQ: 2 HIGH priority processes (Round Robin) and 1 LOW (FCFS).",
    "scheduler": "mlq", "replacer": "fifo", "num_marcos": 4, "quantum": 2,
    "procesos": [
        {"pid": 1, "nombre": "System-A", "llegada": 0, "rafaga": 4, "nivel_mlq": "ALTA"},
        {"pid": 2, "nombre": "System-B", "llegada": 0, "rafaga": 4, "nivel_mlq": "ALTA"},
        {"pid": 3, "nombre": "Batch", "llegada": 0, "rafaga": 6, "nivel_mlq": "BAJA"},
    ],
}

# --- 4) Round Robin with quantum ----------------------------------------------
ROUND_ROBIN = {
    "descripcion": "Round Robin with quantum=2: observe time-sharing in Gantt chart.",
    "scheduler": "rr", "replacer": "fifo", "num_marcos": 4, "quantum": 2,
    "procesos": [
        {"pid": 1, "nombre": "T1", "llegada": 0, "rafaga": 5},
        {"pid": 2, "nombre": "T2", "llegada": 0, "rafaga": 3},
        {"pid": 3, "nombre": "T3", "llegada": 1, "rafaga": 6},
    ],
}

# --- 5) CPU / I/O overlap (DMA model) ----------------------------------
IO_OVERLAP = {
    "descripcion": ("CPU/I/O overlap: P1 blocks on long I/O and CPU "
                    "continues working with P2 meanwhile (DMA model)."),
    "scheduler": "fcfs", "replacer": "fifo", "num_marcos": 4, "quantum": 3,
    "procesos": [
        {"pid": 1, "nombre": "ReadDisk", "llegada": 0, "rafaga": 6,
         "io": [{"en_cpu": 2, "dispositivo": "Disk", "duracion": 4}]},
        {"pid": 2, "nombre": "Compute", "llegada": 1, "rafaga": 4},
    ],
}

PRESETS = {
    "basico": BASICO,
    "page_faults": PAGE_FAULTS,
    "mlq": MLQ_DEMO,
    "round_robin": ROUND_ROBIN,
    "io_overlap": IO_OVERLAP,
}

PRESET_DEFECTO = "basico"


# --- 20-process demo (to evaluate/compare algorithms and strategies) -----
# Generated REPRODUCIBLY with fixed seed. Memory somewhat tight so
# allocation strategies (First/Best/Worst-Fit) differ and to
# show memory pressure. No keyboard I/O so Play mode flows; the
# keyboard signal is triggered with UI button.
def _demo20_dict() -> dict:
    from ..core.aleatorio import Generador
    gen = Generador(seed=2026)
    # devices WITHOUT keyboard for automatic I/O generation
    devs_io = ["Disk", "Printer", "Mouse", "Network"]
    procesos = gen.generar_procesos(20, devs_io, llegada_max=12)
    return {
        "descripcion": ("Demo of 20 varied processes (burst, size and priority). "
                        "Basis to compare 4 schedulers and 3 memory strategies."),
        "scheduler": "rr", "quantum": 3, "costo_cambio": 1,
        "estrategia_mem": "first_fit",
        "ram_total": 8192, "ram_so": 1024, "tam_bloque": 256,
        "paginacion_activa": True, "num_marcos": 6, "replacer": "lru",
        "tasa_error": 0.005, "seed": 2026,
        "procesos": procesos,
    }


def listar() -> list:
    items = [{"nombre": k, "descripcion": v["descripcion"]} for k, v in PRESETS.items()]
    items.append({"nombre": "demo20", "descripcion": _demo20_dict()["descripcion"]})
    return items


def cargar(nombre: str) -> MundoConfig:
    if nombre == "demo20":
        return MundoConfig.from_dict(_demo20_dict())
    if nombre not in PRESETS:
        raise KeyError(f"Unknown preset: {nombre}")
    return MundoConfig.from_dict(PRESETS[nombre])


def demo20() -> MundoConfig:
    return MundoConfig.from_dict(_demo20_dict())


def generar_aleatorio(cantidad: int = 10, seed: int = 12345) -> MundoConfig:
    """Generates a reproducible random scenario of `cantidad` processes."""
    from ..core.aleatorio import Generador
    gen = Generador(seed=seed)
    procesos = gen.generar_procesos(cantidad, ["Disk", "Printer", "Mouse", "Network"],
                                    llegada_max=max(4, cantidad // 2))
    return MundoConfig.from_dict({
        "descripcion": f"Random scenario of {cantidad} processes (seed {seed}).",
        "scheduler": "rr", "quantum": 3, "costo_cambio": 1,
        "estrategia_mem": "first_fit",
        "ram_total": 16384, "ram_so": 2048, "tam_bloque": 256,
        "paginacion_activa": True, "num_marcos": 6, "replacer": "lru",
        "tasa_error": 0.005, "seed": seed, "procesos": procesos,
    })


def config_por_defecto() -> MundoConfig:
    return cargar(PRESET_DEFECTO)
