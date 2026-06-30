# Pipeline de Atualização Mensal — CGEO-CAR

Pipeline simples em Python que **regenera o `index.html` do dashboard** a partir de:

- `pipeline/data/data.json` — dados do mês corrente (PI + ranking nacional + histórico)
- `index.html` na raiz — usado como *baseline* estrutural (HTML, CSS, JS, imagens)

## 🚀 Workflow mensal (3 opções)

### Opção A — 100% manual (mais simples)
1. Abrir `pipeline/data/data.json` e atualizar os números do mês.
2. Commit + push.
3. **GitHub Actions roda automaticamente** e regenera o `index.html`. ✅

### Opção B — Semi-automática (via Excel local)
```bash
cd pipeline
pip install -r requirements.txt

python ingest.py \
  --excel "C:/Downloads/Planilha_Secretario.xlsx" \
  --uf-csv "data/uf_ranking_julho.csv" \
  --month "Julho" --year 2026 \
  --prev-month-short "Jun/26"

python build.py
git add ../index.html pipeline/data/data.json
git commit -m "data: Jul/26"
git push
```

### Opção C — Tudo no GitHub (sem clone local)
1. Editar `pipeline/data/data.json` direto pela web do GitHub.
2. Commit pela web.
3. Actions regenera. ✅

## 📂 Estrutura do `data.json`

```json
{
  "month_long": "Julho",
  "month_short": "Jul/26",
  "previous_month_short": "Jun/26",
  "year": 2026,
  "pi": {
    "total": 334500,
    "ag_gestor": 80000,
    "validados": 55000,
    "cancelados": 2300,
    "pendentes": 195000,
    "suspensos": 3400
  },
  "uf_ranking": { "AC": 1900, "AL": 22000, ... },
  "history": {
    "labels": [...],
    "ag_gestor": [...],
    "validados": [...],
    ...
  },
  "pi_analyses_4mo": { ... }
}
```

## 📥 Formato do CSV de UFs (opcional, para `ingest.py`)

```csv
UF;Total
AC;1885
AL;21103
...
```

## 🔧 Como o `build.py` funciona

1. Lê o `index.html` atual (mantém estrutura, CSS, imagens base64)
2. Lê `data/data.json` (valores do mês)
3. Calcula derivados: percentuais, ranking PI, ranking NE, crescimentos
4. Aplica patches regex em ~50 pontos do HTML:
   - Topbar + section labels
   - Cards de métrica (`data-target`)
   - Breakdowns, status grid, KPIs
   - Texto dos insights (insere números computados)
   - Arrays JS (RANKING, NE, HIST_*, FUNNEL_DATA, etc.)
   - Datasets dos gráficos Chart.js
5. Escreve novo `index.html` na raiz do repo

**Idempotente:** rodar com o mesmo `data.json` produz output equivalente. Você pode testar localmente antes de commitar.

## 🧪 Teste local

```bash
cd pipeline
python build.py --out ../index.html
# verifica se algo mudou:
git diff ../index.html
```

## ⚠️ Limitações conhecidas

- Insights qualitativos (texto livre) podem precisar de revisão humana quando o quadro muda muito.
- O `maxRankVal` (escala visual da barra) está fixo em `1282653` — ajuste no `build.py` se necessário.

---
**Setor de Elaboração:** CGEO / SEMARH-PI
