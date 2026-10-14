// Comparison modal: queries /api/comparativa and builds two tables (schedulers
// and memory strategies), highlighting best value for each metric and with
// CSV export.
const $ = (id) => document.getElementById(id);
let datos = null;   // last comparison loaded

// metric -> [label, "min"|"max"]  ("better" direction)
const MET_SCHED = {
  espera: ["Average wait", "min"], retorno: ["Average turnaround", "min"],
  respuesta: ["Average response", "min"], con_error: ["Processes with error", "min"],
};
const MET_MEM = {
  asignaciones_ok: ["Successful allocations", "max"],
  fallos_externos: ["External fragmentation failures", "min"],
  fragmentacion_interna: ["Internal fragmentation (KB)", "min"],
  huecos_finales: ["Final free holes", "min"],
};

function tablaTranspuesta(titulo, filas, claveCol, mets) {
  const cols = filas.map(f => f.nombre);
  let html = `<div class="comp-tabla"><h3>${titulo}</h3><table><tr><th>Metric</th>`;
  html += cols.map(c => `<th>${c}</th>`).join("") + `</tr>`;
  for (const [met, [etq, dir]] of Object.entries(mets)) {
    const vals = filas.map(f => f[met]);
    const validos = vals.filter(v => v !== null && v !== undefined);
    const mejor = validos.length ? (dir === "min" ? Math.min(...validos) : Math.max(...validos)) : null;
    html += `<tr><td style="text-align:left">${etq}</td>`;
    html += vals.map(v => {
      const txt = (v === null || v === undefined) ? "—" : v;
      const clase = (v !== null && v === mejor) ? " class=\"mejor\"" : "";
      return `<td${clase}>${txt}</td>`;
    }).join("");
    html += `</tr>`;
  }
  html += `</table></div>`;
  return html;
}

function toCSV(filas, mets, claveId) {
  const cabecera = ["algorithm/strategy", ...Object.keys(mets)].join(",");
  const lineas = filas.map(f => [f[claveId], ...Object.keys(mets).map(m => f[m])].join(","));
  return [cabecera, ...lineas].join("\n");
}

function descargar(nombre, contenido) {
  const blob = new Blob([contenido], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(a.href);
}

export async function abrirComparativa() {
  $("comp-tablas").innerHTML = "<p>Calculating…</p>";
  $("modal-comp").classList.remove("oculto");
  try {
    datos = await (await fetch("/api/comparativa")).json();
    $("comp-tablas").innerHTML =
      tablaTranspuesta("🧠 Schedulers (same process set)", datos.schedulers, "algoritmo", MET_SCHED) +
      tablaTranspuesta("💾 Allocation strategies (fragmentation benchmark)", datos.estrategias, "estrategia", MET_MEM);
  } catch (e) {
    $("comp-tablas").innerHTML = `<p style="color:var(--bad)">Calculation error: ${e.message}</p>`;
  }
}

export function initComparativa() {
  $("comp-cerrar").onclick = () => $("modal-comp").classList.add("oculto");
  $("modal-comp").addEventListener("click", e => { if (e.target.id === "modal-comp") $("modal-comp").classList.add("oculto"); });
  $("comp-csv-sched").onclick = () => { if (datos) descargar("comparativa_planificadores.csv", toCSV(datos.schedulers, MET_SCHED, "algoritmo")); };
  $("comp-csv-mem").onclick = () => { if (datos) descargar("comparativa_estrategias.csv", toCSV(datos.estrategias, MET_MEM, "estrategia")); };
}
