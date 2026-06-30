# Dashboard de Análise de Desempenho CAR — SEMARH Piauí

Dashboard interativo de acompanhamento do passivo de análises do Cadastro Ambiental Rural (CAR) no estado do Piauí, com benchmarking nacional entre as 27 UFs.

**Referência:** Junho / 2026 · Fonte SICAR

🔗 **Acesso online:** https://herculesfer1.github.io/CGEO-CAR/

## Conteúdo

- `index.html` — Dashboard completo, single-file, com todos os assets embutidos (gráficos via Chart.js + ícones Lucide via CDN).

## Seções do dashboard

1. **Visão Geral** — Métricas principais do Piauí (Jun/26)
2. **Benchmarking** — Comparativo nacional · ranking das 27 UFs
3. **Funil de Análise** — Fluxo consolidado Gestor → Empreendedor → Resolução
4. **Evolução Temporal** — Série histórica 2022 → 2026
5. **Diagnóstico** — Insights acionáveis e KPIs estratégicos

## Como usar localmente

Basta abrir o `index.html` em qualquer navegador moderno — não há build, servidor ou dependências locais.

## Atualização mensal

Pipeline automatizado em `pipeline/`. Veja [pipeline/README.md](pipeline/README.md).

**Resumo:** edite `pipeline/data/data.json` com os números do novo mês e faça `git push`. O **GitHub Actions** (`.github/workflows/build-dashboard.yml`) regenera o `index.html` automaticamente e o GitHub Pages publica.

---
**Setor de Elaboração:** CGEO / SEMARH-PI
