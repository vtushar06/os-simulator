// PHYSICAL memory (required) in "Physical" tab and paging (PLUS) in
// "Paging" tab.
import { mapProc, nombrePid, hex } from "./state.js";

const $ = (id) => document.getElementById(id);

function fragClase(pct) {
  if (pct > 50) return "bad";
  if (pct >= 20) return "warn";
  return "ok";
}

function renderFisica(snap) {
  const m = snap.memoria_fisica;
  const totalProc = m.ram_total - m.ram_so;
  const pctSO = 100 * m.ram_so / m.ram_total;
  const pctUsada = 100 * m.ram_usada_procesos / m.ram_total;
  const pctLibre = 100 - pctSO - pctUsada;

  const ram = `
    <div class="mem-ram">
      <div class="ram-item"><div class="k">Total RAM</div><div class="v">${m.ram_total} KB</div></div>
      <div class="ram-item"><div class="k">OS RAM</div><div class="v">${m.ram_so} KB</div></div>
      <div class="ram-item"><div class="k">Used by processes</div><div class="v">${m.ram_usada_procesos} KB</div></div>
      <div class="ram-item"><div class="k">Free</div><div class="v">${m.ram_libre} KB</div></div>
    </div>
    <div class="ram-bar">
      <div class="so" style="width:${pctSO}%"></div>
      <div class="proc" style="width:${pctUsada}%"></div>
      <div class="free" style="width:${pctLibre}%"></div>
    </div>
    <div style="font-size:11px;margin-bottom:6px">
      Strategy: <b>${m.estrategia_nombre}</b> · block ${m.tam_bloque} KB · ${m.num_bloques} blocks
      (${m.bloques_so} for OS) &nbsp;
      Internal fragmentation:
      <span class="frag ${fragClase(m.frag_pct)}">${m.fragmentacion} KB (${m.frag_pct}%)</span>
    </div>`;

  const bloques = `<div class="bloques">` + m.bloques.map(b => {
    if (b.tipo === "so") return `<div class="bloque so" title="Block #${b.idx} · OS">OS</div>`;
    if (b.tipo === "libre") return `<div class="bloque libre" title="Block #${b.idx} · free"></div>`;
    return `<div class="bloque" style="background:${b.color}" title="Block #${b.idx} · P${b.pid}">P${b.pid}</div>`;
  }).join("") + `</div>`;

  $("tab-fisica").innerHTML = ram + bloques;
}

function renderPaginacion(snap) {
  const cont = $("tab-paginacion");
  const m = snap.memoria;
  if (!m) {
    cont.innerHTML = `<p style="color:var(--txt2)">Paging (advanced module) is
      <b>disabled</b> in this scenario. Enable it in the process editor.</p>`;
    return;
  }
  const map = mapProc(snap);
  const ct = m.contadores;
  const contadores = `<div class="contadores">
    <div class="c"><b>${ct.aciertos}</b>Hits</div>
    <div class="c"><b>${ct.fallos}</b>Faults</div>
    <div class="c"><b>${(ct.hit_ratio * 100).toFixed(0)}%</b>Hit ratio</div></div>
    <div style="font-size:11px;color:var(--txt2);margin-bottom:5px">
      ${m.algoritmo_nombre} · page ${m.tam_pagina} B · ${m.num_marcos} frames</div>`;

  const ev = m.ultimo_evento_va;
  const marcoFault = (ev && ev.resultado === "FAULT") ? ev.marco : null;
  const marcos = `<div class="marcos">` + m.marcos.map(f => {
    const ptr = (m.algoritmo === "reloj" && m.puntero_reloj === f.idx) ? '<span class="reloj-ptr">👆</span>' : "";
    if (f.pid === null) return `<div class="marco libre"><span>#${f.idx}</span>free${ptr}</div>`;
    const vic = f.idx === marcoFault ? " victima" : "";
    return `<div class="marco${vic}" style="background:${f.color}" title="${nombrePid(map, f.pid)}">
      #${f.idx} P${f.pid}<small>pg ${f.vpn}${f.ref ? " •" : ""}</small>${ptr}</div>`;
  }).join("") + `</div>`;

  let ultimo = '<div class="mem-ultimo"><span style="color:var(--txt2)">No accesses yet.</span></div>';
  if (ev) {
    let txt = `<b>Last access</b> P${ev.pid}: VA ${hex(ev.va)} → VPN ${ev.vpn}+off ${hex(ev.offset)} `;
    if (ev.resultado === "HIT") txt += `→ <b style="color:var(--ok)">HIT</b> · frame ${ev.marco}`;
    else { txt += `→ <b style="color:var(--bad)">FAULT</b>`; if (ev.victima) txt += ` (evicts pg ${ev.victima.vpn} from P${ev.victima.pid})`; }
    ultimo = `<div class="mem-ultimo ${ev.resultado === "HIT" ? "hit" : "fault"}">${txt}</div>`;
  }

  const tablas = m.tablas || {};
  const pids = Object.keys(tablas);
  const tpags = pids.length ? pids.map(pid => {
    const filas = tablas[pid].map(e =>
      `<tr><td>${e.vpn}</td><td>${e.presente ? "yes" : "no"}</td><td>${e.marco !== null ? e.marco : "—"}</td><td>${e.ref ? "1" : "0"}</td></tr>`).join("");
    const color = map[pid] ? map[pid].color : "#fff";
    return `<div class="tpag"><div class="cab" style="color:${color}">P${pid}</div>
      <table><tr><th>VPN</th><th>Pres.</th><th>Frame</th><th>Ref</th></tr>${filas}</table></div>`;
  }).join("") : '<span style="color:var(--txt2);font-size:11px">No tables yet.</span>';

  cont.innerHTML = contadores + marcos + ultimo +
    `<details style="margin-top:6px"><summary style="cursor:pointer;font-size:11px;color:var(--txt2)">Page tables</summary>${tpags}</details>`;
}

export function renderMemoria(snap) {
  renderFisica(snap);
  renderPaginacion(snap);
}
