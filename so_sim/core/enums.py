"""Core enumerations. Inherit from str to serialize directly to JSON."""
from enum import Enum


class Estado(str, Enum):
    NUEVO = "NEW"
    LISTO = "READY"
    EJECUTANDO = "RUNNING"
    BLOQUEADO = "BLOCKED"
    TERMINADO = "TERMINATED"
    ERROR = "ERROR"           # process aborted due to error (see tasa_error)


# State transition diagram (5 states + ERROR). The engine only produces
# these transitions; `transicion_valida()` allows verification (used in tests and
# documented in report). Not enforced at runtime to avoid aborting demo.
TRANSICIONES_VALIDAS = {
    (Estado.NUEVO, Estado.LISTO),          # d) admission (long-term)
    (Estado.LISTO, Estado.EJECUTANDO),     # dispatch
    (Estado.EJECUTANDO, Estado.LISTO),     # b) preemption / quantum expiry (timer)
    (Estado.EJECUTANDO, Estado.BLOQUEADO),  # a) I/O request
    (Estado.EJECUTANDO, Estado.TERMINADO),  # e) burst completion
    (Estado.EJECUTANDO, Estado.ERROR),     # abort due to error
    (Estado.BLOQUEADO, Estado.LISTO),      # c) I/O completion (device interrupt)
}


def transicion_valida(origen: Estado, destino: Estado) -> bool:
    return (origen, destino) in TRANSICIONES_VALIDAS


class SchedAlgo(str, Enum):
    # The 4 required algorithms for SmartLabOS
    FCFS = "fcfs"
    SJF = "sjf"                 # non-preemptive
    PRIORIDAD_NP = "prioridad_np"   # non-preemptive priority
    RR = "rr"


class EstrategiaMem(str, Enum):
    """Contiguous PHYSICAL memory allocation strategies (Required Module 2)."""
    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    WORST_FIT = "worst_fit"


class ReplaceAlgo(str, Enum):
    """Page replacement from PLUS virtual memory module."""
    FIFO = "fifo"
    LRU = "lru"
    OPTIMO = "optimo"
    RELOJ = "reloj"


class TipoDispositivo(str, Enum):
    TECLADO = "keyboard"
    DISCO = "disk"
    IMPRESORA = "printer"
    MOUSE = "mouse"
    RED = "network"


class TipoEvento(str, Enum):
    ADMISION = "admission"
    DESPACHO = "dispatch"
    CAMBIO_CONTEXTO = "context_switch"     # dispatcher work (cost in ticks)
    APROPIACION = "preemption"
    FIN_QUANTUM = "quantum_end"             # timer interrupt
    PAGE_FAULT = "page_fault"
    PAGE_HIT = "page_hit"
    BLOQUEO_IO = "io_block"               # I/O interrupt
    INTERRUPCION_IO = "io_interrupt"     # I/O completion interrupt
    CARGA_MEMORIA = "memory_alloc"         # process loaded into physical memory
    LIBERA_MEMORIA = "memory_free"
    TERMINACION = "termination"
    ABORT_ERROR = "abort_error"             # process terminated with error
    TECLADO_SENAL = "keyboard_signal"         # keyboard requests user decision
    TECLADO_CANCELA = "keyboard_cancel"
    TECLADO_CONTINUA = "keyboard_continue"
    CAMBIO_SCHED = "scheduler_change"
    CAMBIO_REPLACER = "replacer_change"
    CAMBIO_MEM = "memory_strategy_change"               # hot memory strategy change
    RESET = "reset"
    IDLE = "idle"


# Readable names for the interface.
NOMBRE_SCHED = {
    SchedAlgo.FCFS: "FCFS (first come first served)",
    SchedAlgo.SJF: "SJF (shortest job first, non-preemptive)",
    SchedAlgo.PRIORIDAD_NP: "Priority (non-preemptive)",
    SchedAlgo.RR: "Round Robin (quantum)",
}

# The 4 required algorithms that comparison evaluates.
SCHED_OBLIGATORIOS = [SchedAlgo.FCFS, SchedAlgo.SJF, SchedAlgo.PRIORIDAD_NP, SchedAlgo.RR]

NOMBRE_ESTRATEGIA = {
    EstrategiaMem.FIRST_FIT: "First-Fit (first hole)",
    EstrategiaMem.BEST_FIT: "Best-Fit (best fit)",
    EstrategiaMem.WORST_FIT: "Worst-Fit (worst fit)",
}

NOMBRE_REPLACE = {
    ReplaceAlgo.FIFO: "FIFO",
    ReplaceAlgo.LRU: "LRU",
    ReplaceAlgo.OPTIMO: "Optimal (Belady)",
    ReplaceAlgo.RELOJ: "Second chance / Clock",
}
