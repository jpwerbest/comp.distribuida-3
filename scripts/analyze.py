#!/usr/bin/env python3
"""Lê results/*_stats.csv e gera results/summary.csv + gráficos PNG em results/graficos/.
Requer: pip install matplotlib"""
import csv, glob, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
GRAF = os.path.join(BASE, "graficos"); os.makedirs(GRAF, exist_ok=True)
NOMES = {"1": "Cenário 1 - imagem 1MB", "2": "Cenário 2 - texto 400KB", "3": "Cenário 3 - imagem 300KB"}
METRICAS = [("avg", "Tempo médio de resposta (ms)"), ("p95", "Tempo de resposta p95 (ms)"),
            ("rps", "Requisições por segundo"), ("fail", "Taxa de falhas (%)")]

rows = []
for path in glob.glob(os.path.join(BASE, "s*_i*_u*_stats.csv")):
    m = re.search(r"s(\d+)_i(\d+)_u(\d+)_stats\.csv$", path)
    if not m: continue
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r["Name"] == "Aggregated":
            req, fal = float(r["Request Count"]), float(r["Failure Count"])
            rows.append(dict(cenario=m[1], instancias=int(m[2]), usuarios=int(m[3]),
                             requisicoes=int(req), avg=float(r["Average Response Time"]),
                             median=float(r["50%"]), p95=float(r["95%"]), p99=float(r["99%"]),
                             rps=float(r["Requests/s"]), fail=100 * fal / req if req else 0))
if not rows:
    raise SystemExit("Nenhum CSV encontrado em results/")
rows.sort(key=lambda r: (r["cenario"], r["instancias"], r["usuarios"]))
with open(os.path.join(BASE, "summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

def barras(ax, cenario, x_key, s_key, metrica, ylabel, xlabel, leg):
    sub = [r for r in rows if r["cenario"] == cenario]
    xs = sorted({r[x_key] for r in sub}); ss = sorted({r[s_key] for r in sub})
    w = 0.8 / max(len(ss), 1)
    for i, s in enumerate(ss):
        vals = [next((r[metrica] for r in sub if r[x_key] == x and r[s_key] == s), 0) for x in xs]
        pos = [j + i * w - 0.4 + w / 2 for j in range(len(xs))]
        ax.bar(pos, vals, w, label=f"{s} {leg}", edgecolor="black")
    ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend(); ax.grid(axis="y", alpha=.3)

for c in sorted({r["cenario"] for r in rows}):
    for met, label in METRICAS:
        fig, axs = plt.subplots(1, 2, figsize=(13, 4.5))
        barras(axs[0], c, "usuarios", "instancias", met, label, "Número de usuários", "instância(s)")
        barras(axs[1], c, "instancias", "usuarios", met, label, "Número de instâncias", "usuários")
        fig.suptitle(NOMES.get(c, c)); fig.tight_layout()
        fig.savefig(os.path.join(GRAF, f"cenario{c}_{met}.png"), dpi=150); plt.close(fig)
print(f"{len(rows)} execuções processadas. Gráficos em {os.path.abspath(GRAF)}")
