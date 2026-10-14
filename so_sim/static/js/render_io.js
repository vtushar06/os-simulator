// I/O Devices (5): process in service + queue + flash on interrupt.
// Keyboard has a "Signal" button and, if decision is pending, a banner
// with Cancel / Continue. Buttons handled by delegation in controls.js.
import { esc } from "./state.js";

const ICONO = { teclado: "⌨️", disco: "💽", impresora: "🖨️", mouse: "🖱️", red: "🌐" };

export function renderIO(snap) {
  // Devices whose I/O completed this tick (for flash).
  const recien = new Set();
  (snap.eventos || []).forEach(e => {
    if (e.tick === snap.tick && e.tipo === "interrupcion_io") {
      snap.io.dispositivos.forEach(d => { if (e.texto.includes(d.nombre)) recien.add(d.nombre); });
    }
  });

  const cont = document.getElementById("io-dispositivos");
  cont.innerHTML = snap.io.dispositivos.map(d => {
    const ic = ICONO[d.tipo] || "🔌";
    let serv = '<div class="serv" style="color:var(--txt2)">inactive</div>';
    if (d.en_servicio) {
      const s = d.en_servicio;
      const pct = Math.round(s.progreso * 100);
      serv = `<div class="serv">⚙ <b style="color:${s.color}">P${s.pid}</b> ${s.ticks_restantes}/${s.duracion_total}
        <div class="barra-prog"><i style="width:${pct}%;background:${s.color}"></i></div></div>`;
    }
    const cola = d.cola.length
      ? d.cola.map(x => `<span class="chip" style="background:${x.color}">P${x.pid}</span>`).join("")
      : '<span style="color:var(--txt2);font-size:10px">empty queue</span>';
    const btn = d.tipo === "teclado"
      ? `<button class="btn ed-mini btn-teclado-senal" title="Trigger keyboard interrupt">⌨️ Signal</button>`
      : "";
    return `<div class="dispositivo${recien.has(d.nombre) ? " destello" : ""}">
      <div class="nom">${ic} ${esc(d.nombre)} ${btn}</div>
      <div class="tipo">${d.tipo}</div>
      ${serv}<div class="cola-disp">${cola}</div></div>`;
  }).join("");

  const banner = document.getElementById("io-decision");
  const dec = snap.decision_teclado;
  if (dec) {
    banner.classList.remove("oculto");
    banner.innerHTML = `<b>⌨️ Keyboard interrupt</b> on P${dec.pid} (${esc(dec.nombre)}):
      user must decide.
      <div class="acc">
        <button class="btn peligro btn-teclado-cancelar">Cancel process</button>
        <button class="btn primario btn-teclado-continuar">Continue</button>
      </div>`;
  } else {
    banner.classList.add("oculto");
    banner.innerHTML = "";
  }
}
