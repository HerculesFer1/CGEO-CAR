#!/usr/bin/env python3
"""
CGEO-CAR Dashboard Builder
==========================
Regenera o dashboard HTML (index.html) a partir de:
  - baseline.html  (estrutura HTML do dashboard, mantida estavel)
  - data/data.json (dados do mes corrente)

Uso:
  python build.py
  python build.py --data data/data.json --baseline baseline.html --out ../CGEO-CAR/index.html

Setor: CGEO / SEMARH-PI
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Forca UTF-8 no stdout (Windows cp1252 quebra com simbolos especiais)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ─── Mapas de referência ─────────────────────────────────────
REGIONS = {
    "AC":"Norte","AL":"Nordeste","AM":"Norte","AP":"Norte","BA":"Nordeste",
    "CE":"Nordeste","DF":"Centro-Oeste","ES":"Sudeste","GO":"Centro-Oeste",
    "MA":"Nordeste","MG":"Sudeste","MS":"Centro-Oeste","MT":"Centro-Oeste",
    "PA":"Norte","PB":"Nordeste","PE":"Nordeste","PI":"Nordeste","PR":"Sul",
    "RJ":"Sudeste","RN":"Nordeste","RO":"Norte","RR":"Norte","RS":"Sul",
    "SC":"Sul","SE":"Nordeste","SP":"Sudeste","TO":"Norte"
}
NE = {"CE","PI","AL","PB","PE","MA","SE","RN","BA"}

# ─── Formatadores brasileiros ────────────────────────────────
def br_num(n):
    """1234567 → 1.234.567"""
    return f"{int(n):,}".replace(",", ".")

def br_pct(p, decimals=1):
    """27.8 → 27,8"""
    return (f"%.{decimals}f" % p).replace(".", ",")

# ─── Cálculos derivados ──────────────────────────────────────
def compute_derived(data):
    pi = data["pi"]
    total = pi["total"]
    concluidos = pi["pendentes"] + pi["validados"] + pi["cancelados"]
    real_concluidos = pi["validados"] + pi["cancelados"]

    sorted_uf = sorted(
        [{"uf": uf, "value": v, "region": REGIONS[uf]}
         for uf, v in data["uf_ranking"].items() if not uf.startswith("_")],
        key=lambda x: -x["value"]
    )
    pi_rank = next(i+1 for i,r in enumerate(sorted_uf) if r["uf"]=="PI")
    pi_value = next(r["value"] for r in sorted_uf if r["uf"]=="PI")
    ce_value = next(r["value"] for r in sorted_uf if r["uf"]=="CE")
    ne_sorted = [r for r in sorted_uf if r["uf"] in NE]
    pi_ne_rank = next(i+1 for i,r in enumerate(ne_sorted) if r["uf"]=="PI")
    total_brasil = sum(r["value"] for r in sorted_uf)
    ne_total = sum(r["value"] for r in ne_sorted)

    pct = lambda v: v / total * 100
    growth_jan = (pi_value - data["pi_analyses_baseline_jan"]) / data["pi_analyses_baseline_jan"] * 100
    ag_22 = data["history"]["ag_gestor"][0]
    growth_22_26 = (total - ag_22) / ag_22 * 100

    # Cresc. validações Mai→Jun
    val_hist = data["history"]["validados"]
    val_mom = (val_hist[-1] - val_hist[-2]) / val_hist[-2] * 100 if val_hist[-2] else 0
    # Cresc. pendentes Jan→atual
    pend_jan = data["history"]["pendentes"][4]  # Jan/26 is index 4
    pend_now = data["history"]["pendentes"][-1]
    growth_pend = (pend_now - pend_jan) / pend_jan * 100 if pend_jan else 0
    # Maior salto Mai→Jun (Análises Concluídas)
    pend_prev = data["history"]["pendentes"][-2]
    val_prev = data["history"]["validados"][-2]
    canc_prev = data["history"]["cancelados"][-2]
    concl_prev = pend_prev + val_prev + canc_prev
    big_jump = (concluidos - concl_prev) / concl_prev * 100 if concl_prev else 0
    # AG queda Mai→Jun
    ag_prev = data["history"]["ag_gestor"][-2]
    ag_mom = (pi["ag_gestor"] - ag_prev) / ag_prev * 100 if ag_prev else 0
    # AG queda 2025→atual
    ag_25 = data["history"]["ag_gestor"][3]
    ag_25_now = (pi["ag_gestor"] - ag_25) / ag_25 * 100 if ag_25 else 0
    # Necessidade de técnicos
    tecnicos = round(pi["ag_gestor"] / 50 / 12)
    delta_pend = pend_now - pend_prev

    return {
        "total": total, "concluidos": concluidos, "real_concluidos": real_concluidos,
        "pct_ag_gestor": pct(pi["ag_gestor"]), "pct_pendentes": pct(pi["pendentes"]),
        "pct_validados": pct(pi["validados"]), "pct_cancelados": pct(pi["cancelados"]),
        "pct_concluidos": pct(concluidos), "pct_real_concluidos": pct(real_concluidos),
        "sorted_uf": sorted_uf, "ne_sorted": ne_sorted,
        "pi_rank": pi_rank, "pi_ne_rank": pi_ne_rank, "pi_value": pi_value,
        "ce_value": ce_value, "total_brasil": total_brasil,
        "ne_share_pi": pi_value / ne_total * 100 if ne_total else 0,
        "growth_jan": growth_jan, "growth_22_26": growth_22_26,
        "val_mom": val_mom, "growth_pend": growth_pend, "big_jump": big_jump,
        "ag_mom": ag_mom, "ag_25_now": ag_25_now, "tecnicos": tecnicos,
        "delta_pend": delta_pend, "ag_25": ag_25,
    }

# ─── Patches sequenciais ─────────────────────────────────────
def patch(html, pattern, repl, flags=0):
    new_html, n = re.subn(pattern, repl, html, flags=flags)
    if n == 0:
        print(f"  ⚠️  Padrão não encontrado: {pattern[:80]}…")
    return new_html

def build(html, data, d):
    pi = data["pi"]
    m_long = data["month_long"]
    m_short = data["month_short"]
    m_prev = data["previous_month_short"]
    yr = data["year"]

    # ── Topbar e section labels ──
    html = patch(html, r'Referência: \w+ / \d+ · SICAR',
                 f'Referência: {m_long} / {yr} · SICAR')
    html = patch(html, r'Métricas Principais — Piauí · [A-Za-z]+/\d+',
                 f'Métricas Principais — Piauí · {m_short}')
    html = patch(html, r'Comparativo Nacional — Análises Concluídas · [A-Za-z]+/\d+',
                 f'Comparativo Nacional — Análises Concluídas · {m_short}')

    # ── Chart titles ──
    html = patch(html, r'Distribuição do Passivo SICAR — [A-Za-z]+/\d+',
                 f'Distribuição do Passivo SICAR — {m_short}')
    html = patch(html, r'Garante soma perfeita de 100% sobre [\d.]+ registros',
                 f'Garante soma perfeita de 100% sobre {br_num(d["total"])} registros')
    html = patch(html, r'Evolução das Análises — Jan→[A-Za-z]+/\d+',
                 f'Evolução das Análises — Jan→{m_short}')
    html = patch(html, r'Análises concluídas · Referência [A-Za-z]+/\d+',
                 f'Análises concluídas · Referência {m_short}')
    html = patch(html, r'>Análises concluídas · [A-Za-z]+/\d+<',
                 f'>Análises concluídas · {m_short}<')
    html = patch(html, r'Transição Gestor vs Empreendedor — Jan→[A-Za-z]+/\d+',
                 f'Transição Gestor vs Empreendedor — Jan→{m_short}')
    html = patch(html, r"label:'Registros [A-Za-z]+/\d+'",
                 f"label:'Registros {m_short}'")

    # ── Cards: data-target via âncora do label ──
    def card(label, val):
        return patch(
            html_ref[0],
            r'data-target="\d+">0</div>\s*<div class="metric-label">' + re.escape(label),
            f'data-target="{val}">0</div>\n          <div class="metric-label">{label}'
        )
    html_ref = [html]  # truque para closure
    html_ref[0] = card("Total de Registros", d["total"])
    html_ref[0] = card("Aguardando Gestor", pi["ag_gestor"])
    html_ref[0] = card("Análises Concluídas", d["concluidos"])
    html_ref[0] = card("Aguardando Empreendedor", pi["pendentes"])
    html_ref[0] = card("Validados (Regularizados)", pi["validados"])
    html_ref[0] = card("Cancelados", pi["cancelados"])
    html = html_ref[0]

    # ── Breakdown da "Análises Concluídas" ──
    html = patch(html, r'(Ag\. Empreend\.\s*</span>\s*<span class="val">)[\d.]+(</span>)',
                 lambda m: m.group(1) + br_num(pi["pendentes"]) + m.group(2))
    html = patch(html, r'(>\s*Validados\s*</span>\s*<span class="val">)[\d.]+(</span>)',
                 lambda m: m.group(1) + br_num(pi["validados"]) + m.group(2))
    html = patch(html, r'(>\s*Cancelados\s*</span>\s*<span class="val">)[\d.]+(</span>)',
                 lambda m: m.group(1) + br_num(pi["cancelados"]) + m.group(2))

    # ── Percentuais (delta) dos cards ──
    # Aguardando Gestor
    html = patch(html, r'(delta-(?:up|dn|nt|wn))" style="margin-top: auto; width: fit-content;">[\d,]+% do Total</span>\s*</div>\s*</div>\s*<div class="card accent-green">\s*<div class="card-inner">\s*<div class="metric-icon"[^>]*background:rgba\(16,185,129',
                 lambda m: m.group(0).replace(m.group(0)[m.group(0).find('>')+1:m.group(0).find('% do Total')], br_pct(d["pct_ag_gestor"])))
    # Simpler approach: replace each known string
    html = re.sub(r'>27,8% do Total<|>77,2% do Total<', f'>{br_pct(d["pct_ag_gestor"])}% do Total<', html)
    html = re.sub(r'>56,8% do Total<|>10,9% do Total<', f'>{br_pct(d["pct_pendentes"])}% do Total<', html)
    html = re.sub(r'>14,7% do Total<|>11,3% do Total<', f'>{br_pct(d["pct_validados"])}% do Total<', html)
    html = re.sub(r'>0,7% do Total<|>0,6% do Total<', f'>{br_pct(d["pct_cancelados"], 1)}% do Total<', html)

    # ── Ranking PI ──
    pos_label = "Top 25%" if d["pi_rank"] <= 7 else "Top 30%" if d["pi_rank"] <= 9 else "Top 50%"
    html = patch(html, r'<div class="metric-value">#\d+°</div>\s*<div class="metric-label">Ranking Nacional',
                 f'<div class="metric-value">#{d["pi_rank"]}°</div>\n          <div class="metric-label">Ranking Nacional')
    html = patch(html, r'<div class="metric-value">#\d+°</div>\s*<div class="metric-label">Posição no Ranking Nacional',
                 f'<div class="metric-value">#{d["pi_rank"]}°</div>\n          <div class="metric-label">Posição no Ranking Nacional')
    html = re.sub(r'>Top \d+% — Brasil<', f'>{pos_label} — Brasil<', html)
    html = re.sub(r'>Top \d+% entre 27 UFs<', f'>{pos_label} entre 27 UFs<', html)
    html = patch(html, r'#\d+° NE', f'#{d["pi_ne_rank"]}° NE')
    html = patch(html, r'Atrás do CE \([\d.]+\)',
                 f'Atrás do CE ({br_num(d["ce_value"])})')

    # ── Crescimento Jan→{mês} ──
    g = round(d["growth_jan"])
    html = re.sub(r'>\+\d+%</div>\s*<div class="metric-label">Crescimento Jan→\w+<',
                  f'>+{g}%</div>\n          <div class="metric-label">Crescimento Jan→{m_short.split("/")[0]}<', html)
    html = patch(html, r'Crescimento Jan→\w+(?=</div>)', f'Crescimento Jan→{m_short.split("/")[0]}')
    html = patch(html, r'13\.645 → [\d.]+ análises',
                 f'13.645 → {br_num(d["pi_value"])} análises')
    html = patch(html, r'Jan/\d+: 13\.645 → \w+/\d+: [\d.]+',
                 f'Jan/{str(yr)[-2:]}: 13.645 → {m_short}: {br_num(d["pi_value"])}')

    # ── Status grid (Onde está o Passivo?) ──
    html = patch(html, r'(<span class="si-lbl">Aguardando Gestor</span></div>\s*<div class="si-val">)[\d.]+',
                 lambda m: m.group(1) + br_num(pi["ag_gestor"]))
    html = patch(html, r'(<span class="si-lbl">Ag\. Empreendedor</span></div>\s*<div class="si-val">)[\d.]+',
                 lambda m: m.group(1) + br_num(pi["pendentes"]))
    html = patch(html, r'(<span class="si-lbl">Validados</span></div>\s*<div class="si-val">)[\d.]+',
                 lambda m: m.group(1) + br_num(pi["validados"]))
    html = patch(html, r'(<span class="si-lbl">Cancelados</span></div>\s*<div class="si-val">)[\d.]+',
                 lambda m: m.group(1) + br_num(pi["cancelados"]))

    # ── Evolução Temporal cards ──
    g22 = round(d["growth_22_26"])
    html = patch(html, r'>\+\d+%</div>\s*<div class="metric-label">Crescimento Total \(22→26\)',
                 f'>+{g22}%</div>\n          <div class="metric-label">Crescimento Total (22→26)')
    html = patch(html, r'255\.373 → [\d.]+ registros',
                 f'255.373 → {br_num(d["total"])} registros')

    # Maior salto mensal
    html = patch(html, r'>\+[\d,]+%</div>\s*<div class="metric-label">Maior Salto Mensal',
                 f'>+{br_pct(d["big_jump"], 0)}%</div>\n          <div class="metric-label">Maior Salto Mensal')
    html = patch(html, r'(?:Abr|Mar|Mai)→\w+/\d+(?=</span>\s*</div>\s*</div>\s*<div class="card accent-red">)',
                 f'{m_prev.split("/")[0]}→{m_short}')

    # Crescimento de Pendentes
    gp = d["growth_pend"]
    gp_str = f"+{br_pct(gp, 0)}%" if gp < 1000 else f"+{br_pct(gp/100, 1)}×100%"
    if gp >= 1000:
        gp_str = f"+{int(gp):,}%".replace(",", ".")
    html = patch(html, r'>\+[\d.,]+%</div>\s*<div class="metric-label">Crescimento de Pendentes',
                 f'>{gp_str}</div>\n          <div class="metric-label">Crescimento de Pendentes')
    html = patch(html, r'Jan→\w+/\d+(?=</span>\s*</div>\s*</div>\s*</div>\s*<div class="bento bento-2col)',
                 f'Jan→{m_short}')

    # ── Seção Diagnóstico foi removida — KPI strip e insights nao precisam mais ser patcheados.

    # ── JS data block ──
    months4 = data["pi_analyses_4mo"]["labels"]
    html = patch(html, r"const MONTHS4 = \[[^\]]+\];",
                 f"const MONTHS4 = [{','.join(repr(m) for m in months4)}];")
    html = patch(html, r"const PI_ANALYSES = \[[^\]]+\];",
                 f"const PI_ANALYSES = [{','.join(str(v) for v in data['pi_analyses_4mo']['pi'])}];")
    html = patch(html, r"const BRASIL_ANALYSES = \[[^\]]+\];(?: //[^\n]*)?",
                 f"const BRASIL_ANALYSES = [{','.join(str(v) for v in data['pi_analyses_4mo']['brasil'])}];")

    hist = data["history"]
    months_hist = hist["labels"]
    result_months = ["2025"] + months_hist[4:]  # Jan/26 em diante
    html = patch(html, r"const RESULT_MONTHS = \[[^\]]+\];",
                 f"const RESULT_MONTHS = [{','.join(repr(m) for m in result_months)}];")

    # Séries que começam no 2025 (index 3) em diante
    val_series = hist["validados"][3:]
    canc_series = hist["cancelados"][3:]
    pend_series = hist["pendentes"][3:]
    ag_series = hist["ag_gestor"][3:]

    html = patch(html, r"const VALIDADOS  = \[[^\]]+\];",
                 f"const VALIDADOS  = [{','.join(str(v) for v in val_series)}];")
    html = patch(html, r"const CANCELADOS = \[[^\]]+\];",
                 f"const CANCELADOS = [{','.join(str(v) for v in canc_series)}];")
    html = patch(html, r"const PENDENTES  = \[[^\]]+\];(?: //[^\n]*)?",
                 f"const PENDENTES  = [{','.join(str(v) for v in pend_series)}]; // Agrupado Pendentes + Suspensos")
    html = patch(html, r"const AG_GESTOR  = \[[^\]]+\];",
                 f"const AG_GESTOR  = [{','.join(str(v) for v in ag_series)}];")

    # ANOS e TOTAL_REG (anuais + mês atual)
    anos = ["2022","2023","2024","2025", m_short]
    html = patch(html, r"const ANOS = \[[^\]]+\];",
                 f"const ANOS = [{','.join(repr(a) for a in anos)}];")
    html = patch(html, r"const TOTAL_REG = \[[^\]]+\];",
                 f"const TOTAL_REG = [{','.join(str(v) for v in hist['total_anual'])}];")

    # HIST_* (todas as séries)
    html = patch(html, r"const HIST_LABELS = \[[^\]]+\];",
                 f"const HIST_LABELS = [{','.join(repr(m) for m in months_hist)}];")
    html = patch(html, r"const HIST_AG_GESTOR = \[[^\]]+\];",
                 f"const HIST_AG_GESTOR = [{','.join(str(v) for v in hist['ag_gestor'])}];")
    html = patch(html, r"const HIST_VALIDADOS = \[[^\]]+\];",
                 f"const HIST_VALIDADOS = [{','.join(str(v) for v in hist['validados'])}];")
    html = patch(html, r"const HIST_CANCELADOS = \[[^\]]+\];",
                 f"const HIST_CANCELADOS = [{','.join(str(v) for v in hist['cancelados'])}];")
    html = patch(html, r"const HIST_PENDENTES = \[[^\]]+\];",
                 f"const HIST_PENDENTES = [{','.join(str(v) for v in hist['pendentes'])}];")
    html = patch(html, r"const HIST_SUSPENSOS = \[[^\]]+\];",
                 f"const HIST_SUSPENSOS = [{','.join(str(v) for v in hist['suspensos'])}];")

    # RANKING e NE
    ranking_str = ",\n  ".join(
        f"{{r:{i+1},e:'{r['uf']}',reg:'{r['region']}',v:{r['value']}}}"
        for i,r in enumerate(d["sorted_uf"])
    )
    html = patch(html, r"const RANKING = \[[\s\S]*?\];",
                 f"const RANKING = [\n  {ranking_str}\n];")
    ne_str = ",".join(f"{{e:'{r['uf']}',v:{r['value']}}}" for r in d["ne_sorted"])
    html = patch(html, r"const NE = \[[\s\S]*?\];", f"const NE = [{ne_str}];")

    # FUNNEL_DATA
    funnel = (
        "const FUNNEL_DATA = [\n"
        f"  {{label:'Total de Registros', val:{d['total']}, pct:100.0, color:'#94A3B8'}},\n"
        f"  {{label:'Ag. Gestor (passivo)', val:{pi['ag_gestor']}, pct:{round(d['pct_ag_gestor'],1)}, color:'#EF4444'}},\n"
        f"  {{label:'Ag. Empreendedor', val:{pi['pendentes']}, pct:{round(d['pct_pendentes'],1)}, color:'#F59E0B'}},\n"
        f"  {{label:'Validados', val:{pi['validados']}, pct:{round(d['pct_validados'],1)}, color:'#10B981'}},\n"
        f"  {{label:'Cancelados', val:{pi['cancelados']}, pct:{round(d['pct_cancelados'],1)}, color:'#3B82F6'}},\n"
        "];"
    )
    html = patch(html, r"const FUNNEL_DATA = \[[\s\S]*?\];", funnel)

    # Share denominador
    html = patch(html, r"\(row\.v/\d+\*100\)", f"(row.v/{d['total_brasil']}*100)")

    # Donut labels
    pct_str = lambda v: br_pct(v)
    donut_labels = (f"['Aguardando Gestor ({pct_str(d['pct_ag_gestor'])}%)',"
                    f"'Aguardando Empreendedor ({pct_str(d['pct_pendentes'])}%)',"
                    f"'Validados ({pct_str(d['pct_validados'])}%)',"
                    f"'Cancelados ({pct_str(d['pct_cancelados'])}%)']")
    html = patch(html, r"labels:\['Aguardando Gestor[^\]]+\]", f"labels:{donut_labels}")
    html = patch(html, r"data:\[\d+, \d+, \d+, \d+\]",
                 f"data:[{pi['ag_gestor']}, {pi['pendentes']}, {pi['validados']}, {pi['cancelados']}]", flags=re.MULTILINE)

    # Pie de responsabilidade
    resp_labels = (f"['Passivo Gestor ({pct_str(d['pct_ag_gestor'])}%)',"
                   f"'Passivo Empreend. ({pct_str(d['pct_pendentes'])}%)',"
                   f"'Concluídos Reais ({pct_str(d['pct_real_concluidos'])}%)']")
    html = patch(html, r"labels:\['Passivo Gestor[^\]]+\]", f"labels:{resp_labels}")
    html = patch(html, r"data:\[\d+,\d+,\d+\]",
                 f"data:[{pi['ag_gestor']},{pi['pendentes']},{d['real_concluidos']}]")

    # Monthly bars (Validados, Ag.Empreendedor, Cancelados — últimos 4 meses)
    val4 = hist["validados"][-4:]
    pend4 = hist["pendentes"][-4:]
    canc4 = hist["cancelados"][-4:]
    html = patch(html, r"\{label:'Validados',data:\[[\d,]+\]",
                 f"{{label:'Validados',data:[{','.join(str(v) for v in val4)}]")
    html = patch(html, r"\{label:'Ag\. Empreendedor',data:\[[\d,]+\]",
                 f"{{label:'Ag. Empreendedor',data:[{','.join(str(v) for v in pend4)}]")
    html = patch(html, r"\{label:'Cancelados',data:\[[\d,]+\]",
                 f"{{label:'Cancelados',data:[{','.join(str(v) for v in canc4)}]")

    return html

# ─── CLI ─────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/data.json")
    p.add_argument("--baseline", default="baseline.html",
                   help="HTML base (estrutura). Por padrão, baseline.html.")
    p.add_argument("--out", default="../CGEO-CAR/index.html",
                   help="HTML final. Por padrão sobrescreve o do repo.")
    args = p.parse_args()

    here = Path(__file__).parent
    data = json.loads((here / args.data).read_text(encoding="utf-8"))
    baseline_path = here / args.baseline
    if not baseline_path.exists():
        # Fallback: usa o próprio output como baseline (preserva estrutura)
        baseline_path = here / args.out
    html = baseline_path.read_text(encoding="utf-8")

    d = compute_derived(data)
    print(f"▸ Rank PI Nacional: #{d['pi_rank']}° · NE: #{d['pi_ne_rank']}° · Total Brasil: {br_num(d['total_brasil'])}")
    print(f"▸ PI Total: {br_num(d['total'])} · AG: {br_pct(d['pct_ag_gestor'])}% · Pend: {br_pct(d['pct_pendentes'])}% · Val: {br_pct(d['pct_validados'])}%")

    new_html = build(html, data, d)

    out_path = (here / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_html, encoding="utf-8")
    print(f"✓ Dashboard gerado: {out_path}")

if __name__ == "__main__":
    main()
