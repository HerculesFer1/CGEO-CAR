# Dashboard de Análise de Desempenho CAR — SEMARH-PI

Painel interativo de monitoramento do **Cadastro Ambiental Rural (CAR)** do Piauí, desenvolvido pela **CGEO/SEMARH-PI** para acompanhamento mensal do desempenho do estado nas análises de imóveis rurais.

## Sobre o Projeto

O CAR é um registro eletrônico nacional obrigatório para imóveis rurais, integrante do Sistema Nacional de Informações sobre o Meio Ambiente (SICAR). Este dashboard consolida os dados do SICAR-PI e do ranking nacional de análises para apoio à gestão e à tomada de decisão.

## Estrutura do Repositório

```
├── 0. Backup/          Dashboards históricos de referência (Abril 2026)
├── 1.Database/         Arquivos de dados por competência (CSV/XLSX)
├── 2. Resultado/       Dashboards publicados por mês
└── logo-piaui.png      Logotipo institucional
```

## Dashboards Disponíveis

| Competência | Arquivo | Destaques |
|-------------|---------|-----------|
| Junho 2026  | `2. Resultado/1. Dashboard de Análise de Desempenho CAR(Junho 2026).html` | PI: **#6 nacional · #2 Nordeste** · 49.815 análises · 334.881 registros |
| Maio 2026   | `2. Resultado/1. Dashboard de Análise de Desempenho CAR(Maio 2026).html`  | PI: **#8 nacional · #2 Nordeste** · 25.497 análises |
| Abril 2026  | `0. Backup/1. Dashboard de Análise de Desempenho CAR - Abril.html`        | PI: **#8 nacional · #2 Nordeste** · 24.297 análises |

## Indicadores Monitorados

- **Total de registros ativos** no SICAR-PI
- **FASE CAR**: Aguardando Gestor · Aguardando Empreendedor · Validados · Cancelados
- **Ranking nacional** por análises concluídas (27 estados)
- **Ranking Nordeste** por análises concluídas (9 estados)
- Evolução histórica mensal (gráficos de linha, barra e rosca)
- Participação do PI no total nacional de análises

## Metodologia

O ranking utiliza como métrica o **total de análises concluídas** (Validados + Cancelados) por UF, conforme dados do SICAR federal — garantindo consistência metodológica entre competências. Os dados SICAR-PI são extraídos via relatório de busca de imóveis e confrontados com o consolidado nacional por UF.

## Tecnologias

- HTML5 / CSS3 / JavaScript (vanilla)
- [Chart.js](https://www.chartjs.org/) — gráficos interativos
- Animações de contagem via `IntersectionObserver`

## Fonte dos Dados

- **SICAR-PI**: Relatório de Busca de Imóveis — exportação mensal
- **SICAR Nacional**: Consolidado de análises por UF — exportação mensal

---

**CGEO — Coordenadoria de Geoprocessamento**  
Secretaria de Meio Ambiente e Recursos Hídricos do Piauí (SEMARH-PI)
