// Metrics per process (wait/turnaround/response) + averages + error count.

export function renderMetricas(snap) {
  const ps = snap.procesos;
  const pr = snap.metricas;

  const resumen = `<div class="metr-resumen">
    <div class="m"><b>${pr.terminados}/${pr.total}</b>terminated</div>
    <div class="m ok"><b>${pr.terminados_ok ?? 0}</b>OK</div>
    <div class="m err"><b>${pr.con_error ?? 0}</b>with error</div>
  </div>`;

  const filas = ps.map(p => {
    const m = p.metricas;
    return `<tr>
      <td><span class="dotpid" style="background:${p.color}"></span>P${p.pid}</td>
      <td>${m.espera}</td>
      <td>${m.retorno !== null ? m.retorno : "—"}</td>
      <td>${m.respuesta !== null ? m.respuesta : "—"}</td>
    </tr>`;
  }).join("");

  const prom = (pr.retorno !== null)
    ? `<tr class="prom"><td>Average</td><td>${pr.espera}</td><td>${pr.retorno}</td>
       <td>${pr.respuesta !== null ? pr.respuesta : "—"}</td></tr>`
    : `<tr class="prom"><td colspan="4">No process has completed yet…</td></tr>`;

  document.getElementById("tabla-metricas").innerHTML = resumen +
    `<table><tr><th>Proc</th><th>Wait</th><th>Turnaround</th><th>Response</th></tr>${filas}${prom}</table>`;
}
