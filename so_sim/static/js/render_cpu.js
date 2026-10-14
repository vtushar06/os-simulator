// CPU panel: running process, Program Counter (large and animated per tick),
// progress bar, algorithm/quantum and context switch notice.
import { esc } from "./state.js";

const $ = (id) => document.getElementById(id);
let pcAnterior = null;

export function renderCPU(snap) {
  const c = snap.cpu;
  $("cpu-alg").textContent = c.algoritmo_nombre +
    (c.quantum ? ` · q=${c.quantum}` : "");

  let avatar, datos, barra = "";
  if (c.pid_ejecutando !== null && c.pid_ejecutando !== undefined) {
    avatar = `<div class="cpu-avatar" style="background:${c.color_ejecutando}">P${c.pid_ejecutando}</div>`;
    datos = `<div class="cpu-datos"><b>${esc(c.nombre_ejecutando || ("P"+c.pid_ejecutando))}</b><br>
      <small>PID ${c.pid_ejecutando} · CPU ${c.cpu_consumido}/${c.rafaga_total}
      ${c.quantum_restante !== null && c.quantum_restante !== undefined ? "· q.rem " + c.quantum_restante : ""}</small></div>`;
    const prog = c.rafaga_total ? Math.round(100 * c.cpu_consumido / c.rafaga_total) : 0;
    barra = `<div class="cpu-barra"><i style="width:${prog}%;background:${c.color_ejecutando}"></i></div>`;
  } else {
    avatar = `<div class="cpu-avatar idle">idle</div>`;
    datos = `<div class="cpu-datos"><b>CPU idle</b><br><small>no process running</small></div>`;
  }

  const ctx = c.cambiando_contexto
    ? `<div class="ctx-badge">🔄 context switch in progress…</div>` : "";
  const disp = `<div class="disp-info">Dispatcher: ${snap.dispatcher.total_cambios} context switches
    (cost ${snap.dispatcher.costo_cambio} tick/switch)</div>`;

  $("cpu-actual").innerHTML = `
    <div class="cpu-proc">${avatar}${datos}</div>
    ${barra}
    <div class="pc-caja"><div class="etq">Program Counter (PC)</div>
      <div class="pc-valor" id="pc-valor">${c.pc ?? 0}</div></div>
    ${ctx}${disp}`;

  // PC animation when value changes
  const pcEl = $("pc-valor");
  if (pcEl && c.pc !== pcAnterior) {
    pcEl.classList.add("tic");
    setTimeout(() => pcEl.classList.remove("tic"), 120);
    pcAnterior = c.pc;
  }
}
