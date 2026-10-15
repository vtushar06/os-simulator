// Event log with color badges by type, recent events highlighted and utilities
// for Clear (client) and Export .txt.
import { esc } from "./state.js";

const BADGE = {
  io_interrupt: ["be-io", "I/O"], io_block: ["be-io", "I/O"],
  quantum_end: ["be-reloj", "Timer"], preemption: ["be-reloj", "Timer"],
  abort_error: ["be-abort", "Abort"], termination: ["be-otro", "End"],
  context_switch: ["be-ctx", "Context"],
  keyboard_signal: ["be-teclado", "Keyboard"], keyboard_cancel: ["be-teclado", "Keyboard"],
  keyboard_continue: ["be-teclado", "Keyboard"],
  page_fault: ["be-otro", "Pg.Fault"], page_hit: ["be-otro", "Pg.Hit"],
  admission: ["be-otro", "Admission"], dispatch: ["be-otro", "Dispatch"],
  memory_alloc: ["be-otro", "Mem"], memory_free: ["be-otro", "Mem"],
  scheduler_change: ["be-otro", "Config"], replacer_change: ["be-otro", "Config"],
  memory_strategy_change: ["be-otro", "Config"],
};

let minTick = 0;          // events with tick < minTick are "cleared" (client)
let ultimos = [];         // last events shown (for export)

export function limpiarLog(snap) { minTick = (snap ? snap.tick : 0) + 1; render([]); }
export function resetLog() { minTick = 0; }

export function exportarLog() {
  const txt = ultimos.map(e => `[Tick ${String(e.tick).padStart(3, "0")}] [${e.tipo}] ${e.texto}`).join("\n");
  const blob = new Blob([txt || "(no events)"], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "event_log_os.txt";
  a.click();
  URL.revokeObjectURL(a.href);
}

function render(eventos) {
  const items = eventos.slice().reverse();
  document.getElementById("bitacora").innerHTML = items.map((e, i) => {
    const [cls, etq] = BADGE[e.tipo] || ["be-otro", e.tipo];
    const reciente = i < 3 ? " reciente" : "";
    return `<li class="${reciente}">
      <span class="t mono">${e.tick}</span>
      <span class="badge-ev ${cls}">${etq}</span>
      <span>${esc(e.texto)}</span></li>`;
  }).join("");
}

export function renderLog(snap) {
  ultimos = (snap.eventos || []).filter(e => e.tick >= minTick);
  render(ultimos);
}
