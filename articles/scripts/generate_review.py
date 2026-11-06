#!/usr/bin/env python3
"""Генерация подробного обзора articles/review/review.tex по данным двух дашбордов.

Все числа берутся из CSV в articles/raw/, поэтому обзор пересобирается
вместе с дашбордами: python3 articles/scripts/generate_review.py
Сборка PDF: cd articles/review && latexmk -xelatex review.tex
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "review" / "review.tex"
MPEST = "pysatl-mpest"
WEIGHT = {"yes": 1.0, "partial": 0.5, "no": 0.0}

CATEGORY_NAMES = {
    "estimation": "Оценивание",
    "structure": "Структура смеси",
    "initialization": "Инициализация",
    "technical": "Архитектура",
    "infrastructure": "Инфраструктура",
    "visualization": "Визуализация",
    "proprietary": "Специальные методы",
    "representation": "Представление смеси",
    "performance": "Производительность",
    "diagnostics": "Диагностика",
}
PRIORITY_NAMES = {"must": "обязательные", "should": "желательные", "could": "факультативные"}
MIXTURE = {"homogeneous": "однородная", "heterogeneous": "разнородная"}
MORPH = {
    "symmetric": "симметричные",
    "skewed": "асимметричные",
    "semi_bounded": "положительный носитель",
    "heavy_tailed": "тяжёлый хвост",
}
SAMPLE = {"small": "малая", "moderate": "умеренная", "large": "большая", "massive": "очень большая"}


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


_TEX = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def esc(text: object) -> str:
    return "".join(_TEX.get(c, c) for c in str(text))


def lc(text: str) -> str:
    """Строчная первая буква, если слово не аббревиатура."""
    if len(text) > 1 and text[1].islower():
        return text[0].lower() + text[1:]
    return text


def plural(n: int, one: str, few: str, many: str) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def pct(value: float) -> str:
    return f"{round(value * 100)} %"


tools = read(RAW / "reqs/tools.csv")
reqs = read(RAW / "requirements.csv")
evals = read(RAW / "reqs/evaluations.csv")
req_articles = read(RAW / "reqs/requirement_articles.csv")
articles = read(RAW / "articles.csv")
ucs = read(RAW / "usecases/usecases.csv")
uc_reqs = read(RAW / "usecases/usecase_requirements.csv")
uc_articles = read(RAW / "usecases/usecase_articles.csv")

status = {(e["tool_id"], e["req_id"]): e["status"] for e in evals}
tool_ids = [t["tool_id"] for t in tools]
tool_name = {t["tool_id"]: t["name"] for t in tools}
tool_eco = {t["tool_id"]: t["ecosystem"] for t in tools}
req = {r["req_id"]: r for r in reqs}
others = [t for t in tool_ids if t != MPEST]
assert len(evals) == len(tools) * len(reqs), "матрица оценок неполна"


def yes_count(req_id: str, group: list[str] | None = None) -> int:
    return sum(status[(t, req_id)] == "yes" for t in (group or others))


def partial_count(req_id: str, group: list[str] | None = None) -> int:
    return sum(status[(t, req_id)] == "partial" for t in (group or others))


def score(tool: str, req_ids: list[str]) -> float:
    return sum(WEIGHT[status[(tool, r)]] for r in req_ids) / len(req_ids)


# ---------------------------------------------------------------- расчёты
by_cat: dict[str, list[str]] = defaultdict(list)
for r in reqs:
    by_cat[r["type"]].append(r["req_id"])
cat_order = [c for c in CATEGORY_NAMES if c in by_cat]

tool_counts = {t: Counter(status[(t, r["req_id"])] for r in reqs) for t in tool_ids}
total_score = {t: score(t, [r["req_id"] for r in reqs]) for t in tool_ids}
must_ids = [r["req_id"] for r in reqs if r["priority"] == "must"]
should_ids = [r["req_id"] for r in reqs if r["priority"] == "should"]
could_ids = [r["req_id"] for r in reqs if r["priority"] == "could"]

none_full = [r["req_id"] for r in reqs if yes_count(r["req_id"], tool_ids) == 0]
rare = [r["req_id"] for r in reqs if 0 < yes_count(r["req_id"], tool_ids) <= 2]
common = [r["req_id"] for r in reqs if yes_count(r["req_id"]) >= 20]

hetero_tools = [t for t in others if status[(t, "STRUC-02")] == "yes"]
hetero_partial = [t for t in others if status[(t, "STRUC-02")] == "partial"]
hetero_all = hetero_tools + [MPEST]

ecm_hetero = [t for t in hetero_all if status[(t, "EST-02")] == "yes"]
ecme_hetero = [t for t in hetero_all if status[(t, "EST-03")] == "yes"]
full_pack = [t for t in hetero_all if all(status[(t, r)] == "yes" for r in ("INIT-02", "STRUC-09", "EST-12", "EST-13"))]
bootstrap_hetero = [t for t in hetero_all if status[(t, "STRUC-11")] == "yes"]
config_hetero = [t for t in hetero_all if status[(t, "STRUC-13")] == "yes"]

uc_info = {}
for u in ucs:
    uid = u["usecase_id"]
    crit = [x["req_id"] for x in uc_reqs if x["usecase_id"] == uid and x["importance"] == "critical"]
    desi = [x["req_id"] for x in uc_reqs if x["usecase_id"] == uid and x["importance"] == "desirable"]
    sc = {t: score(t, crit) for t in tool_ids}
    full = [t for t in tool_ids if all(status[(t, r)] == "yes" for r in crit)]
    best = sorted(sc.items(), key=lambda kv: (-kv[1], kv[0]))
    uc_info[uid] = {"crit": crit, "desi": desi, "score": sc, "full": full, "best": best}

crit_freq = Counter(x["req_id"] for x in uc_reqs if x["importance"] == "critical")
uc_ref_reqs = {x["req_id"] for x in uc_reqs}
datasets = {(x["usecase_id"], x["dataset_name"]) for x in uc_articles if x["dataset_name"]}

gaps = []
for r in reqs:
    rid = r["req_id"]
    if status[(MPEST, rid)] == "yes":
        continue
    gaps.append(
        (
            rid,
            status[(MPEST, rid)],
            yes_count(rid),
            sum(1 for u in ucs if rid in uc_info[u["usecase_id"]]["crit"]),
            sum(1 for u in ucs if rid in uc_info[u["usecase_id"]]["desi"]),
        )
    )
prio_rank = {"must": 0, "should": 1, "could": 2}
gaps.sort(key=lambda g: (prio_rank[req[g[0]]["priority"]], -g[3], -g[4], -g[2], g[0]))
only_mpest = [r["req_id"] for r in reqs if status[(MPEST, r["req_id"])] == "yes" and yes_count(r["req_id"]) == 0]
mpest_rank = sorted(tool_ids, key=lambda t: -total_score[t]).index(MPEST) + 1
mpest_must = score(MPEST, must_ids)
best_other_must = max((score(t, must_ids), t) for t in others)

n_art_req = len({x["article_id"] for x in req_articles})
n_art_uc = len({x["article_id"] for x in uc_articles})
n_art_all = len(articles)
n_art_union = len({x["article_id"] for x in req_articles} | {x["article_id"] for x in uc_articles})



# ---------------------------------------------------------------- производные величины
ucs_hetero = [u["usecase_id"] for u in ucs if u["mixture_type"] == "heterogeneous"]
best_per_uc = {uid: uc_info[uid]["best"][0] for uid in uc_info}
mpest_top_ucs = [uid for uid, (t, _) in best_per_uc.items() if t == MPEST]
no_full_uc = all(not uc_info[uid]["full"] for uid in uc_info)
critical_total = len({x["req_id"] for x in uc_reqs if x["importance"] == "critical"})
ecm_hetero = [t for t in hetero_all if status[(t, "EST-02")] == "yes"]
ecme_hetero = [t for t in hetero_all if status[(t, "EST-03")] == "yes"]
full_pack = [t for t in hetero_all if all(status[(t, r)] == "yes" for r in ("INIT-02", "STRUC-09", "EST-12", "EST-13"))]
bootstrap_hetero = [t for t in hetero_all if status[(t, "STRUC-11")] == "yes"]
config_hetero = [t for t in hetero_all if status[(t, "STRUC-13")] == "yes"]
must_gaps = [g for g in gaps if req[g[0]]["priority"] == "must" and g[1] == "no"]
crit_gaps = [r for r in sorted(crit_freq) if status[(MPEST, r)] != "yes" and crit_freq[r] >= 2]
mean_best = sum(uc_info[u["usecase_id"]]["best"][0][1] for u in ucs) / len(ucs)
no_partial = [r for r in none_full if partial_count(r, tool_ids) == 0]


# ================================================================ расширенный обзор (LaTeX)
import itertools
import re

tools_by_id = {t["tool_id"]: t for t in tools}
art = {a["article_id"]: a for a in articles}


def pct(value: float) -> str:  # noqa: F811
    return f"{round(value * 100)}\\,\\%"


def T(x: object) -> str:
    return r"\texttt{" + esc(x) + "}"


def tt(tool_id: str) -> str:
    return T(tool_name[tool_id])


def tts(ids: list[str]) -> str:
    return ", ".join(tt(t) for t in ids) or "---"


def rn(rid: str) -> str:
    return esc(lc(req[rid]["name"]))


def rl(rid: str) -> str:
    return T(rid) + " " + esc(req[rid]["name"])


def hm(value: float) -> str:
    return rf"\cellcolor{{hm!{round(5 + 70 * value)}}}{round(value * 100)}"


def link(url: str) -> str:
    url = url.strip()
    if url.startswith("http"):
        return r"\url{" + url.replace("%", r"\%").replace("#", r"\#") + "}"
    if not url or url.lower() in ("none", "nan"):
        return "---"
    return r"\texttt{" + esc(url).replace("/", "/\\allowbreak{}") + "}"


def rot(text: str) -> str:
    return r"\rotatebox{90}{\scriptsize " + text + "}"


MARK = {"yes": r"\cellcolor{yes!35}+", "partial": r"\cellcolor{part!45}$\pm$", "no": r"\textcolor{gray}{·}"}
STATUS_TEX = {
    "yes": r"\cellcolor{yes!30}да",
    "partial": r"\cellcolor{part!40}част.",
    "no": r"\textcolor{gray}{нет}",
}
STATUS_WORD = {"yes": "выполнено", "partial": "частично", "no": "не выполнено"}


def st(tool: str, rid: str) -> str:
    return STATUS_TEX[status[(tool, rid)]]


def author_short(authors: str) -> str:
    names = [a.strip() for a in authors.split(";") if a.strip()]
    if not names:
        return "---"
    if len(names) <= 2:
        return ", ".join(names)
    return names[0] + " и др."


def art_ref(aid: str) -> str:
    a = art.get(aid)
    if not a:
        return T(aid)
    return f"{esc(author_short(a['authors']))} ({esc(a['year'])}). {esc(a['title'])} " + r"\textit{[" + esc(aid) + "]}"


SAMPLE_FULL = {"small": "малая (до сотни наблюдений)", "moderate": "умеренная (сотни--тысячи)", "large": "большая (десятки тысяч)", "massive": "очень большая (миллионы)"}
PRIOR = {
    "unknown_k_separated": "число компонент неизвестно, компоненты разделены",
    "unknown_k_overlapping": "число компонент неизвестно, компоненты перекрываются",
    "known_k_overlapping": "число компонент известно, компоненты перекрываются",
    "known_k_separated": "число компонент известно, компоненты разделены",
    "known_k_competing": "число компонент известно, механизмы конкурируют",
    "known_k_heterogeneous": "число компонент известно, семейства разнородны",
    "unknown_k_heterogeneous": "число компонент неизвестно, семейства разнородны",
}
OBS = {"direct": "прямые наблюдения", "censored": "цензурированные наблюдения", "imbalanced": "несбалансированные веса компонент", "binned": "сгруппированные данные"}
ROLE_ART = {"foundation": "основа", "method": "метод", "benchmark": "эталонные данные"}
ROLE_CASE = {"primary_benchmark": "первичный эталон", "validation": "валидация", "application": "применение"}

# ---------------------------------------------------------------- дополнительные расчёты
ALL_REQ = [r["req_id"] for r in reqs]


def wscore(tool: str, req_ids: list[str], wp: float) -> float:
    vals = {"yes": 1.0, "partial": wp, "no": 0.0}
    return sum(vals[status[(tool, r)]] for r in req_ids) / len(req_ids)


def rank_by(fn) -> dict[str, int]:
    order = sorted(tool_ids, key=lambda t: (-fn(t), t))
    return {t: i + 1 for i, t in enumerate(order)}


rank_w = {wp: rank_by(lambda t, wp=wp: wscore(t, ALL_REQ, wp)) for wp in (0.0, 0.5, 1.0)}
PRIO_W = {"must": 3, "should": 2, "could": 1}


def prio_score(tool: str) -> float:
    num = sum(PRIO_W[req[r]["priority"]] * WEIGHT[status[(tool, r)]] for r in ALL_REQ)
    den = sum(PRIO_W[req[r]["priority"]] for r in ALL_REQ)
    return num / den


rank_prio = rank_by(prio_score)
rank_must = rank_by(lambda t: score(t, must_ids))
rank_should = rank_by(lambda t: score(t, should_ids))
rank_could = rank_by(lambda t: score(t, could_ids))
rank_total = rank_by(lambda t: total_score[t])
yes_sets = {t: {r for r in ALL_REQ if status[(t, r)] == "yes"} for t in tool_ids}


def jaccard(a: str, b: str) -> float:
    u = yes_sets[a] | yes_sets[b]
    return len(yes_sets[a] & yes_sets[b]) / len(u) if u else 0.0


nearest = {}
for t in tool_ids:
    cand = sorted(((jaccard(t, o), o) for o in tool_ids if o != t), key=lambda x: (-x[0], x[1]))
    nearest[t] = cand[:3]

multivariate = [t["tool_id"] for t in tools if "многомерн" in t["description"].lower()]


def set_cover(uid: str):
    crit = set(uc_info[uid]["crit"])
    left = set(crit)
    chosen = []
    while left:
        best = max(tool_ids, key=lambda t: (len(left & yes_sets[t]), t == MPEST, t))
        gain = left & yes_sets[best]
        if not gain:
            break
        chosen.append((best, len(gain)))
        left -= gain
    return chosen, left


covers = {u["usecase_id"]: set_cover(u["usecase_id"]) for u in ucs}

# выигрыш от закрытия пробела mpest (средний прирост покрытия критических требований по сценариям)
gain = {}
for rid, stt, ycnt, ncrit, ndes in gaps:
    g = 0.0
    for u in ucs:
        info = uc_info[u["usecase_id"]]
        if rid in info["crit"]:
            g += (1 - WEIGHT[status[(MPEST, rid)]]) / len(info["crit"])
    gain[rid] = g / len(ucs)
gap_by_gain = sorted((g for g in gaps if gain[g[0]] > 0), key=lambda g: (-gain[g[0]], prio_rank[req[g[0]]["priority"]], g[0]))
base_mean = sum(uc_info[u["usecase_id"]]["score"][MPEST] for u in ucs) / len(ucs)
mpest_after_must = {}
for t_ in [MPEST]:
    def after(close: set[str]) -> tuple[float, float]:
        vals = {"yes": 1.0, "partial": 0.5, "no": 0.0}
        def sc(req_ids):
            return sum(1.0 if r in close else vals[status[(MPEST, r)]] for r in req_ids) / len(req_ids)
        m = sum(sc(uc_info[u["usecase_id"]]["crit"]) for u in ucs) / len(ucs)
        return m, sc(ALL_REQ)
    mpest_after_must = after({g[0] for g in gaps if req[g[0]]['priority'] == 'must'})
    mpest_after_crit = after(set(crit_freq))
    curve = []
    closed: set[str] = set()
    for g in gap_by_gain[:12]:
        closed.add(g[0])
        curve.append((g[0], after(closed)[0]))

crit_cat_share = {}
for u in ucs:
    c = Counter(req[r]["type"] for r in uc_info[u["usecase_id"]]["crit"])
    crit_cat_share[u["usecase_id"]] = c

# ---------------------------------------------------------------- вывод
out: list[str] = []
w = out.append
hetero_partial_ids = hetero_partial

w(r"""\documentclass[10pt,a4paper]{article}
\usepackage[a4paper,margin=1.8cm]{geometry}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{russian}
\setotherlanguage{english}
\setmainfont{CMU Serif}
\setsansfont{CMU Sans Serif}
\setmonofont{CMU Typewriter Text}
\usepackage{amsmath}
\usepackage[table]{xcolor}
\usepackage{booktabs,longtable,array,graphicx,pdflscape,hyperref,enumitem,fancyhdr,titlesec,needspace}
\definecolor{hm}{RGB}{31,111,235}
\definecolor{yes}{RGB}{26,127,55}
\definecolor{part}{RGB}{210,153,34}
\hypersetup{colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!50!black,citecolor=blue!50!black}
\urlstyle{tt}
\setlist{itemsep=1pt,topsep=3pt}
\setlength{\parindent}{1.0cm}
\setlength{\parskip}{0pt}
\renewcommand{\arraystretch}{1.12}
\sloppy\emergencystretch=3em
\setcounter{tocdepth}{2}
\setcounter{secnumdepth}{3}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection}{0.6em}{}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Обзор инструментов и сценариев}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\newcommand{\lab}[1]{\par\noindent\textbf{#1.}\ }
\title{Подробный обзор инструментов оценивания конечных смесей\\и прикладных сценариев}
\author{}
\date{}
\begin{document}
\maketitle
""")

# ------------------------------------------------ аннотация, оглавление
n_yes_total = sum(1 for e in evals if e["status"] == "yes")
n_part_total = sum(1 for e in evals if e["status"] == "partial")
n_no_total = sum(1 for e in evals if e["status"] == "no")
w(
    rf"""\begin{{abstract}}\noindent
В документе подробно разобрана эмпирическая база обзора: {len(tools)} инструментов оценивания конечных смесей, {len(reqs)} требований к библиотеке
и {len(ucs)} прикладных сценариев. Документ не повторяет основной текст работы, а дополняет его: содержит матрицы покрытия по каждой категории требований, сопоставление разнородных средств,
анализ чувствительности оценок, сходство инструментов по профилю возможностей, расчёт приоритетов развития \texttt{{{MPEST}}}. Описания отдельных инструментов, требований и сценариев,
обоснование и ссылка для каждой из {len(evals)} оценок, а также связанные публикации приведены в дашбордах и здесь не дублируются. Все числа вычислены из таблиц базы, на которой построены два дашборда.
Интерактивные версии базы: дашборд инструментов и требований (\texttt{{dashboard.html}}) и дашборд сценариев (\texttt{{usecases\_dashboard.html}}).
\end{{abstract}}
\tableofcontents
\clearpage
"""
)

# ------------------------------------------------ краткие выводы
w(
    rf"""\section*{{Краткие выводы}}
\addcontentsline{{toc}}{{section}}{{Краткие выводы}}
\begin{{enumerate}}
\item \textbf{{Нет инструмента, закрывающего потребности сценариев целиком.}} Для каждого из {len(ucs)} сценариев определены критические требования
({critical_total} различных требований); {'ни один из ' + str(len(tools)) + ' инструментов не выполняет полностью критические требования ни одного сценария' if no_full_uc else 'полное покрытие есть не везде'}.
Лучший инструмент для сценария в среднем закрывает {pct(mean_best)} его критических требований.
\item \textbf{{Разнородные смеси полностью поддерживают {len(hetero_all)} {plural(len(hetero_all), 'средство', 'средства', 'средств')} из {len(tools)}:}}
{tts(hetero_all)}; ещё {len(hetero_partial)} --- частично ({tts(hetero_partial)}).
Схему ECME среди них реализует только {tts(ecme_hetero)}; блочная схема ECM есть у {tts(ecm_hetero)}.
\item \textbf{{{len(none_full)} из {len(reqs)} требований не выполнено полностью ни одним инструментом}}, ещё {len(rare)} выполнены не более чем двумя;
базовый слой (EM, нормальное семейство, логарифмическая устойчивость, сборка и тесты) есть почти у всех.
\item \textbf{{Положение \texttt{{{MPEST}}}.}} Обязательные требования выполнены на {pct(mpest_must)} (лучший из остальных --- {tt(best_other_must[1])}, {pct(best_other_must[0])});
по всем требованиям {mpest_rank}-е место из {len(tools)}. В разнородных сценариях {', '.join(mpest_top_ucs) or '---'} он лидирует; в однородных гауссовых уступает зрелым пакетам.
\item \textbf{{Приоритеты развития}} следуют из двух списков: обязательные требования, не выполненные библиотекой
({'; '.join(rn(g[0]) for g in must_gaps)}), и расчёт выигрыша по сценариям (раздел~\ref{{sec:roadmap}}).
\item \textbf{{Ограничения:}} оценки получены по документации и коду без запуска программ и характеризуют заявленные возможности, а не качество; сценарии --- классы задач, а не полная выборка.
\end{{enumerate}}
"""
)

# ================================================================ ЧАСТЬ I
w(r"\part{Данные и методика}")
w(
    rf"""\section{{Эмпирическая база}}
\subsection{{Состав}}
База состоит из связанных таблиц; ссылочная целостность между ними поддерживается.
\begin{{center}}\small
\begin{{tabular}}{{@{{}}l p{{9.2cm}} r@{{}}}}
\toprule
Таблица базы & Содержание & Записей \\
\midrule
Инструменты & язык, репозиторий, лицензия, публикация, описание & {len(tools)} \\
Требования & категория, название, описание, источник, приоритет & {len(reqs)} \\
Оценки & статус, обоснование и ссылка для каждой пары <<инструмент --- требование>> & {len(evals)} \\
Связи требований с публикациями & роли публикаций: основа, метод, эталонные данные & {len(req_articles)} \\
Публикации & авторы, год, цитирования, ссылки, воспроизводимость & {len(articles)} \\
Сценарии & описание и характеристики данных и смеси & {len(ucs)} \\
Требования сценариев & критические и желательные требования с обоснованием & {len(uc_reqs)} \\
Публикации и наборы данных сценариев & публикации и наборы данных, на которых основан сценарий & {len(uc_articles)} \\
\bottomrule
\end{{tabular}}
\end{{center}}
Матрица оценок полна: {len(tools)} $\times$ {len(reqs)} $=$ {len(evals)} строк. Распределение статусов: выполнено --- {n_yes_total} ({pct(n_yes_total / len(evals))}),
частично --- {n_part_total} ({pct(n_part_total / len(evals))}), не выполнено --- {n_no_total} ({pct(n_no_total / len(evals))}).
К {len([e for e in evals if e['evidence_link'].strip()])} из {len(evals)} оценок приложена ссылка на документацию или код.

\subsection{{Как собиралась база}}
Каталог требований составлен по инструментам: сначала разобраны {len(tools)} инструментов и их возможности оформлены как атомарные требования; затем из статей
добавлены специфичные методы, которых в инструментах нет. Приоритеты: обязательные --- базовые архитектурные и математические требования ядра ({len(must_ids)}),
желательные --- важные конкурентные возможности ({len(should_ids)}), факультативные --- исследовательские и специализированные методы из статей ({len(could_ids)}).
Сценарии выбирались по публикациям; затем проверялось, какие требования нужны сценарию и какие инструменты их выполняют.
Из {n_art_all} публикаций реестра {n_art_union} связаны с требованиями или сценариями ({n_art_req} --- с требованиями, {n_art_uc} --- со сценариями).

\subsection{{Границы предметной области}}
В область работы входят только конечные смеси одномерных непрерывных распределений, однородные и разнородные. Вне области: многомерные смеси,
дискретные смеси и смеси с точечной массой, регрессионные смеси с ковариатами, модели латентных классов, скрытые марковские модели, модели дискретного выбора,
многоуровневые модели. Оценки инструментов выставлены по одним и тем же требованиям независимо от этих границ, поэтому инструменты, рассчитанные прежде всего
на многомерные данные ({tts(multivariate) if multivariate else '---'}), оцениваются по тому, что они дают в одномерном случае.

\section{{Правила подсчёта}}
\subsection{{Покрытие}}
Покрытие группы требований инструментом --- среднее значение весов: выполнено $=1$, частично $=\tfrac12$, не выполнено $=0$. Показатель отражает заявленные возможности по
документации и коду; программы не запускались, поэтому он не измеряет качество оценивания. В разделах про сценарии покрытие считается по критическим требованиям сценария.

\subsection{{Чувствительность к весу частичных оценок}}
Вес $\tfrac12$ для частично выполненных требований --- условность. В таблице показано, как меняется место инструмента при весах $0$ (частично не засчитывается),
$\tfrac12$ и $1$ (частично приравнивается к выполненному), а также при взвешивании по приоритетам (обязательные $\times 3$, желательные $\times 2$, факультативные $\times 1$).
{{\footnotesize
\begin{{longtable}}{{@{{}}l r r r r r r r r@{{}}}}
\toprule
Инструмент & $w{{=}}0$ & $w{{=}}\tfrac12$ & $w{{=}}1$ & По приоритетам & Обяз. & Жел. & Факульт. & Разброс \\
\midrule
\endhead
{chr(10).join(rf"{esc(tool_name[t])} & {rank_w[0.0][t]} & {rank_w[0.5][t]} & {rank_w[1.0][t]} & {rank_prio[t]} & {rank_must[t]} & {rank_should[t]} & {rank_could[t]} & {max(rank_w[0.0][t], rank_w[0.5][t], rank_w[1.0][t], rank_prio[t]) - min(rank_w[0.0][t], rank_w[0.5][t], rank_w[1.0][t], rank_prio[t])} \\" for t in sorted(tool_ids, key=lambda x: rank_w[0.5][x]))}
\bottomrule
\end{{longtable}}}}
Места определяются по убыванию покрытия; у равных значений порядок произвольный. Наиболее устойчивые лидеры по всем схемам:
{tts([t for t in sorted(tool_ids, key=lambda x: rank_w[0.5][x]) if max(rank_w[0.0][t], rank_w[0.5][t], rank_w[1.0][t], rank_prio[t]) <= 5][:5])}.
Положение \texttt{{{MPEST}}}: {rank_w[0.0][MPEST]}-е при $w{{=}}0$, {rank_w[0.5][MPEST]}-е при $w{{=}}\tfrac12$, {rank_w[1.0][MPEST]}-е при $w{{=}}1$, {rank_prio[MPEST]}-е с весами приоритетов;
по обязательным требованиям {rank_must[MPEST]}-е, по желательным {rank_should[MPEST]}-е, по факультативным {rank_could[MPEST]}-е.

\subsection{{Ограничения методики}}
\begin{{itemize}}
\item Оценки выставлены по документации и коду; поведение программ не измерялось. Вывод об отсутствии возможности относится к рассмотренным интерфейсам и версиям.
\item Равные веса требований внутри приоритета не отражают разную трудоёмкость реализации.
\item Набор из {len(ucs)} сценариев иллюстрирует классы задач и не исчерпывает их; сценарии выбирались по публикациям с открытыми данными.
\item Статус \texttt{{{MPEST}}} соответствует состоянию на дату оценки.
\end{{itemize}}
"""
)

# ================================================================ ЧАСТЬ II. ИНСТРУМЕНТЫ
w(r"\part{Инструменты}")
w(r"\section{Каталог}")
cat_rows = []
for t in tools:
    cat_rows.append(
        rf"{esc(t['name'])} & {esc(t['ecosystem'])} & {esc(t['license'])} & {'рассм.' if t['status'] == 'reviewed' else 'канд.'} & {link(t['repository_url'])} \\"
    )
w(
    r"""Список инструментов в порядке реестра. Статус: <<рассм.>> --- инструмент разобран по документации и коду, <<канд.>> --- кандидат, оценён по документации.
{\footnotesize
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{4.2cm} >{\raggedright\arraybackslash}p{1.8cm} >{\raggedright\arraybackslash}p{2.3cm} l >{\raggedright\arraybackslash}p{6.2cm}@{}}
\toprule
Инструмент & Язык & Лицензия & Статус & Репозиторий \\
\midrule
\endhead
"""
    + "\n".join(cat_rows)
    + r"""
\bottomrule
\end{longtable}}
"""
)
w(
    rf"""\subsection{{Распределение по языкам и лицензиям}}
\begin{{center}}\small
\begin{{tabular}}{{@{{}}l r l r@{{}}}}
\toprule
Язык & Инструментов & Лицензия & Инструментов \\
\midrule
{chr(10).join(f"{esc(a)} & {n} & {esc(b)} & {m} \\\\" for (a, n), (b, m) in itertools.zip_longest(Counter(tool_eco[t] for t in tool_ids).most_common(), Counter(tools_by_id[t]['license'] for t in tool_ids).most_common(), fillvalue=('', '')))}
\bottomrule
\end{{tabular}}
\end{{center}}
"""
)

# --- ландшафт: общая сводная таблица
cat_head = " & ".join(rot(esc(CATEGORY_NAMES[c])) for c in cat_order)
rows = []
for tid in sorted(tool_ids, key=lambda x: rank_w[0.5][x]):
    c = tool_counts[tid]
    cells = [
        str(rank_w[0.5][tid]),
        r"\textbf{" + esc(tool_name[tid]) + "}" + (r" (цель)" if tid == MPEST else ""),
        esc(tool_eco[tid]),
        str(c["yes"]),
        str(c["partial"]),
        str(c["no"]),
        hm(total_score[tid]),
        hm(score(tid, must_ids)),
        hm(score(tid, should_ids)),
        hm(score(tid, could_ids)),
    ] + [hm(score(tid, by_cat[cat])) for cat in cat_order]
    rows.append(" & ".join(cells) + r" \\")
w(r"\begin{landscape}")
w(
    rf"""\section{{Сводная таблица покрытия}}
Инструменты упорядочены по общему покрытию (вес частичных $\tfrac12$). Числа в цветных ячейках --- проценты; чем темнее ячейка, тем выше покрытие.
Обозначения: <<Да>>, <<Част.>>, <<Нет>> --- число требований с соответствующим статусом (из {len(reqs)}).
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}r l l r r r r r r r *{{{len(cat_order)}}}{{r}}@{{}}}}
\toprule
\# & Инструмент & Язык & {rot('Да')} & {rot('Част.')} & {rot('Нет')} & {rot('Все, \\%')} & {rot('Обяз., \\%')} & {rot('Жел., \\%')} & {rot('Факульт., \\%')} & {cat_head} \\
\midrule
\endhead
{chr(10).join(rows)}
\bottomrule
\end{{longtable}}}}
Спектр узкий: наибольшее покрытие достигает {pct(max(total_score[t] for t in tool_ids))} ({tt(max(tool_ids, key=lambda x: total_score[x]))}),
медиана составляет {pct(sorted(total_score.values())[len(tools) // 2])}; у {sum(1 for v in total_score.values() if v < 0.5)} из {len(tools)} инструментов покрытие ниже половины.
"""
)
w(r"\end{landscape}")

# --- ближайшие по профилю
w(
    rf"""\section{{Сходство инструментов по профилю возможностей}}
Для каждого инструмента найдены три ближайших по мере Жаккара над множествами полностью выполненных требований. Значение $1$ означает совпадение профилей,
$0$ --- отсутствие общих выполненных требований. Это показывает, какие инструменты заменяют друг друга и какие занимают отдельные ниши.
{{\footnotesize
\begin{{longtable}}{{@{{}}>{{\raggedright\arraybackslash}}p{{3.8cm}} >{{\raggedright\arraybackslash}}p{{12.4cm}}@{{}}}}
\toprule
Инструмент & Ближайшие (мера Жаккара) \\
\midrule
\endhead
{chr(10).join(rf"{esc(tool_name[t])} & " + ", ".join(f"{esc(tool_name[o])} ({v:.2f})" for v, o in nearest[t]) + r" \\" for t in sorted(tool_ids, key=lambda x: rank_w[0.5][x]))}
\bottomrule
\end{{longtable}}}}
Наиболее похожая пара: {tt(max(((jaccard(a, b), a, b) for a, b in itertools.combinations(tool_ids, 2)))[1])} и {tt(max(((jaccard(a, b), a, b) for a, b in itertools.combinations(tool_ids, 2)))[2])}
({max(((jaccard(a, b), a, b) for a, b in itertools.combinations(tool_ids, 2)))[0]:.2f}). Ближайший к \texttt{{{MPEST}}} инструмент: {tt(nearest[MPEST][0][1])} ({nearest[MPEST][0][0]:.2f});
профиль \texttt{{{MPEST}}} не совпадает ни с одним из рассмотренных ({'расстояние до ближайшего велико' if nearest[MPEST][0][0] < 0.5 else 'близок к ' + esc(tool_name[nearest[MPEST][0][1]])}).
"""
)

# ================================================================ ЧАСТЬ III. ТРЕБОВАНИЯ
w(r"\part{Требования}")
cat_rows = []
for cat in cat_order:
    ids = by_cat[cat]
    ys = sum(yes_count(r) for r in ids)
    ps = sum(partial_count(r) for r in ids)
    mean_cov = (ys + 0.5 * ps) / (len(ids) * len(others))
    zero = sum(1 for r in ids if yes_count(r, tool_ids) == 0)
    cat_rows.append(
        rf"{esc(CATEGORY_NAMES[cat])} & {len(ids)} & {sum(req[r]['priority'] == 'must' for r in ids)} & {sum(req[r]['priority'] == 'should' for r in ids)} & {sum(req[r]['priority'] == 'could' for r in ids)} & {hm(mean_cov)} & {zero} & {hm(score(MPEST, ids))} \\"
    )
w(
    rf"""\section{{Общая картина}}
\begin{{center}}\small
\begin{{tabular}}{{@{{}}l r r r r r r r@{{}}}}
\toprule
Категория & Всего & Обяз. & Жел. & Фак. & \shortstack[r]{{\scriptsize Среднее покрытие\\\scriptsize инструментами, \%}} & \shortstack[r]{{\scriptsize Выполнено\\\scriptsize никем}} & \shortstack[r]{{\scriptsize Покрытие\\\scriptsize \texttt{{mpest}}, \%}} \\
\midrule
{chr(10).join(cat_rows)}
\bottomrule
\end{{tabular}}
\end{{center}}
Покрытие считается по {len(others)} инструментам без \texttt{{{MPEST}}}.

\subsection{{Распределение требований по числу инструментов}}
Сколько требований выполняют полностью ровно $k$ инструментов (из {len(others)}, без \texttt{{{MPEST}}}).
{{\small
\begin{{center}}
\begin{{tabular}}{{@{{}}l {'r' * 9}@{{}}}}
\toprule
Число инструментов & 0 & 1 & 2 & 3--4 & 5--7 & 8--11 & 12--15 & 16--19 & 20+ \\
\midrule
Требований & {' & '.join(str(sum(1 for r in ALL_REQ if lo <= yes_count(r) <= hi)) for lo, hi in [(0, 0), (1, 1), (2, 2), (3, 4), (5, 7), (8, 11), (12, 15), (16, 19), (20, 99)])} \\
\bottomrule
\end{{tabular}}
\end{{center}}}}
Распределение сильно скошено: {len(common)} требований выполняют не менее 20 инструментов, а {len([r for r in ALL_REQ if yes_count(r) <= 2])} --- не более двух.

\subsection{{Что умеют почти все}}
Не менее 20 из {len(others)} инструментов полностью выполняют: {'; '.join(rl(r) for r in common)}.
Это базовый слой, который любая новая библиотека обязана воспроизвести, но отличие на нём не строится.

\subsection{{Что не умеет никто}}
Ни один из {len(tools)} инструментов полностью не выполняет {len(none_full)} требований: {'; '.join(rl(r) for r in none_full)}.
{len(none_full) - len(no_partial)} из них реализуются хотя бы частично (для отдельных семейств или как расширение);
{len(no_partial)} {plural(len(no_partial), 'не представлено', 'не представлены', 'не представлены')} даже частично: {'; '.join(rn(r) for r in no_partial) or '---'}.

\subsection{{Что умеют единицы}}
Не более двух инструментов, включая \texttt{{{MPEST}}}, полностью выполняют {len(rare)} требований: {'; '.join(rl(r) for r in rare)}.
"""
)

# --- матрицы по категориям (ландшафт)
w(r"\begin{landscape}")
w(r"\section{Матрицы покрытия по категориям}")
w(
    r"""Для каждой категории требований показаны статусы всех инструментов. Условные обозначения: \colorbox{yes!35}{+} --- выполнено,
\colorbox{part!45}{$\pm$} --- частично, \textcolor{gray}{·} --- не выполнено. Столбцы обозначены идентификаторами требований; расшифровка идёт под таблицей.
"""
)
tool_order = sorted(tool_ids, key=lambda x: rank_w[0.5][x])
for cat in cat_order:
    ids = by_cat[cat]
    header = " & ".join(rot(esc(r)) for r in ids)
    rows = []
    for t in tool_order:
        rows.append(esc(tool_name[t]) + " & " + " & ".join(MARK[status[(t, r)]] for r in ids) + r" \\")
    rows.append(r"\midrule " + r"\textit{Выполнено, шт.} & " + " & ".join(str(yes_count(r, tool_ids)) for r in ids) + r" \\")
    keyrows = [rf"\texttt{{{esc(r)}}} & {esc(req[r]['name'])} & {esc(PRIORITY_NAMES[req[r]['priority']])}" for r in ids]
    half = (len(keyrows) + 1) // 2
    pairs = []
    for i in range(half):
        left = keyrows[i]
        right = keyrows[i + half] if i + half < len(keyrows) else " & & "
        pairs.append(left + " & " + right + r" \\")
    w(
        rf"""\subsection{{{esc(CATEGORY_NAMES[cat])}}}
{{\scriptsize\setlength{{\tabcolsep}}{{2.2pt}}
\begin{{longtable}}{{@{{}}l *{{{len(ids)}}}{{c}}@{{}}}}
\toprule
Инструмент & {header} \\
\midrule
\endhead
{chr(10).join(rows)}
\bottomrule
\end{{longtable}}}}
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{tabular}}{{@{{}}l >{{\raggedright\arraybackslash}}p{{7.4cm}} l l >{{\raggedright\arraybackslash}}p{{7.4cm}} l@{{}}}}
{chr(10).join(pairs)}
\end{{tabular}}}}
"""
    )
w(r"\end{landscape}")

# ================================================================ ЧАСТЬ IV. СЦЕНАРИИ
w(r"\part{Прикладные сценарии}")
w(r"\section{Характеристики сценариев}")
uc_rows = []
for u in ucs:
    uid = u["usecase_id"]
    info = uc_info[uid]
    uc_rows.append(
        rf"\textbf{{{esc(uid)}}} & {esc(u['domain'])} & {esc(MIXTURE[u['mixture_type']])} & {esc(MORPH[u['component_morphology']])} & {esc(PRIOR.get(u['prior_knowledge'], u['prior_knowledge']))} & {esc(OBS.get(u['observation_regime'], u['observation_regime']))} & {esc(SAMPLE[u['sample_regime']])} & {len(info['crit'])} & {len(info['desi'])} \\"
    )
w(
    rf"""Каждый сценарий описывается пятью признаками: типом смеси (однородная или разнородная), формой компонент, априорными сведениями о числе и разделимости компонент,
режимом наблюдения и объёмом выборки. В последних колонках --- число критических и желательных требований.
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}l >{{\raggedright\arraybackslash}}p{{2.7cm}} >{{\raggedright\arraybackslash}}p{{1.5cm}} >{{\raggedright\arraybackslash}}p{{1.9cm}} >{{\raggedright\arraybackslash}}p{{3.3cm}} >{{\raggedright\arraybackslash}}p{{2.5cm}} >{{\raggedright\arraybackslash}}p{{1.6cm}} r r@{{}}}}
\toprule
ID & Область & Смесь & Компоненты & Априорные сведения & Режим наблюдения & Выборка & Крит. & Жел. \\
\midrule
\endhead
{chr(10).join(uc_rows)}
\bottomrule
\end{{longtable}}}}
Состав: однородных сценариев --- {sum(1 for u in ucs if u['mixture_type'] == 'homogeneous')}, разнородных --- {sum(1 for u in ucs if u['mixture_type'] == 'heterogeneous')};
по форме компонент: {', '.join(f'{esc(MORPH[k])} --- {v}' for k, v in Counter(u['component_morphology'] for u in ucs).most_common())};
по выборке: {', '.join(f'{esc(SAMPLE[k])} --- {v}' for k, v in Counter(u['sample_regime'] for u in ucs).most_common())}.
"""
)

# --- матрица требование x сценарий
ref_reqs = sorted(uc_ref_reqs, key=lambda r: (cat_order.index(req[r]["type"]), r))
mrows = []
for rid in ref_reqs:
    cells = []
    for u in ucs:
        imp = next((x["importance"] for x in uc_reqs if x["usecase_id"] == u["usecase_id"] and x["req_id"] == rid), None)
        cells.append(r"\cellcolor{hm!70}К" if imp == "critical" else (r"\cellcolor{hm!22}Ж" if imp else ""))
    nc = crit_freq.get(rid, 0)
    mrows.append(
        rf"{T(rid)} & {esc(req[rid]['name'])} & " + " & ".join(cells) + rf" & {nc} & {sum(1 for x in uc_reqs if x['req_id'] == rid and x['importance'] == 'desirable')} & {yes_count(rid, tool_ids)} & {st(MPEST, rid)} \\"
    )
w(r"\begin{landscape}")
w(
    rf"""\section{{Требования сценариев}}
Таблица связывает {len(ref_reqs)} требований, на которые ссылаются сценарии (из {len(reqs)}), со сценариями: К --- критическое, Ж --- желательное. Справа:
число сценариев с критическим и желательным требованием, число инструментов с полным выполнением и статус \texttt{{{MPEST}}}.
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}l >{{\raggedright\arraybackslash}}p{{8.2cm}} *{{{len(ucs)}}}{{c}} r r r l@{{}}}}
\toprule
ID & Требование & {' & '.join(esc(u['usecase_id'].replace('UC-', '')) for u in ucs)} & Крит. & Жел. & Инстр. & \texttt{{mpest}} \\
\midrule
\endhead
{chr(10).join(mrows)}
\bottomrule
\end{{longtable}}}}
Столбцы 01--10 --- номера сценариев UC-01--UC-10.
"""
)
w(r"\end{landscape}")

w(
    rf"""\section{{Структура критических требований}}
Распределение критических требований сценариев по категориям показывает, какие группы возможностей определяют пригодность инструмента для конкретной задачи.
{{\small
\begin{{longtable}}{{@{{}}l {'r' * len(cat_order)}@{{}}}}
\toprule
Сценарий & {' & '.join(rot(esc(CATEGORY_NAMES[c])) for c in cat_order)} \\
\midrule
\endhead
{chr(10).join(esc(u['usecase_id']) + ' & ' + ' & '.join(str(crit_cat_share[u['usecase_id']].get(c, 0) or '') for c in cat_order) + r' \\' for u in ucs)}
\bottomrule
\end{{longtable}}}}
"""
)

# --- покрытие и минимальные наборы
w(
    rf"""\section{{Покрытие сценариев инструментами}}
\subsection{{Покрытие критических требований}}
Значение --- доля критических требований сценария, выполненных инструментом (частично выполненные с весом $\tfrac12$).
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}l *{{{len(ucs) + 1}}}{{r}}@{{}}}}
\toprule
Инструмент & {' & '.join(esc(u['usecase_id']) for u in ucs)} & Ср. \\
\midrule
\endhead
{chr(10).join(esc(tool_name[t]) + ' & ' + ' & '.join(hm(uc_info[u['usecase_id']]['score'][t]) for u in ucs) + ' & ' + hm(sum(uc_info[u['usecase_id']]['score'][t] for u in ucs) / len(ucs)) + r' \\' for t in sorted(tool_ids, key=lambda x: -sum(uc_info[u['usecase_id']]['score'][x] for u in ucs)))}
\bottomrule
\end{{longtable}}}}
Лучший инструмент для сценария в среднем закрывает {pct(mean_best)} его критических требований; полное покрытие {'отсутствует у всех инструментов во всех сценариях' if no_full_uc else 'есть не везде'}.

\subsection{{Сколько инструментов нужно, чтобы закрыть сценарий}}
Если ни один инструмент не закрывает критические требования сценария полностью, возникает вопрос, сколько инструментов пришлось бы совмещать.
Жадный подбор: на каждом шаге выбирается инструмент, полностью выполняющий наибольшее число ещё не закрытых критических требований. Результат --- верхняя оценка
размера набора и показатель разрозненности возможностей.
{{\footnotesize
\begin{{longtable}}{{@{{}}l r >{{\raggedright\arraybackslash}}p{{8.8cm}} >{{\raggedright\arraybackslash}}p{{3.6cm}}@{{}}}}
\toprule
Сценарий & Набор & Инструменты (сколько критических требований добавляет) & Не закрыто \\
\midrule
\endhead
{chr(10).join(esc(u['usecase_id']) + ' & ' + str(len(covers[u['usecase_id']][0])) + ' & ' + ', '.join(esc(tool_name[t]) + ' (' + str(n) + ')' for t, n in covers[u['usecase_id']][0]) + ' & ' + ('; '.join(esc(r) for r in sorted(covers[u['usecase_id']][1])) or '---') + r' \\' for u in ucs)}
\bottomrule
\end{{longtable}}}}
Среднее число инструментов в наборе: {sum(len(covers[u['usecase_id']][0]) for u in ucs) / len(ucs):.1f}. Сценарии, у которых после подбора остаются полностью не выполненные никем требования:
{', '.join(esc(u['usecase_id']) for u in ucs if covers[u['usecase_id']][1]) or 'нет'}.
Это значит, что для сценария либо нужно совмещать несколько пакетов (и вручную согласовывать форматы моделей), либо дописывать недостающее.
"""
)

# ================================================================ ЧАСТЬ V. РАЗНОРОДНЫЕ СМЕСИ
w(r"\part{Разнородные смеси}")
w(r"\begin{landscape}")
het_set = hetero_all + hetero_partial_ids
rows = []
for cat in cat_order:
    rows.append(r"\midrule \multicolumn{" + str(len(het_set) + 2) + r"}{@{}l}{\textbf{" + esc(CATEGORY_NAMES[cat]) + "}} \\\\")
    for rid in by_cat[cat]:
        rows.append(rf"{T(rid)} & {esc(req[rid]['name'])} & " + " & ".join(st(t, rid) for t in het_set) + r" \\")
w(
    rf"""\section{{Полное сопоставление средств для разнородных смесей}}
Разнородные смеси, где компоненты принадлежат разным семействам, --- основной сценарий библиотеки. Полностью допускают их {len(hetero_tools)} {plural(len(hetero_tools), 'инструмент', 'инструмента', 'инструментов')} кроме \texttt{{{MPEST}}}:
{tts(hetero_tools)}; частично --- {tts(hetero_partial)}. Таблица сопоставляет все {len(reqs)} требований для этих {len(het_set)} средств.
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}l >{{\raggedright\arraybackslash}}p{{8.0cm}} *{{{len(het_set)}}}{{c}}@{{}}}}
\toprule
ID & Требование & {' & '.join(rot(esc(tool_name[t])) for t in het_set)} \\
\midrule
\endhead
{chr(10).join(rows)}
\bottomrule
\end{{longtable}}}}
"""
)
w(r"\end{landscape}")
het_cov_rows = []
for t in het_set:
    het_cov_rows.append(
        rf"{esc(tool_name[t])} & {'полностью' if t in hetero_all else 'частично'} & {hm(total_score[t])} & {hm(score(t, must_ids))} & {sum(1 for r in ucs_hetero if t in [x for x, _ in uc_info[r]['best'][:3]])} & {hm(sum(uc_info[r]['score'][t] for r in ucs_hetero) / len(ucs_hetero))} \\"
    )
w(
    rf"""\section{{Выводы по разнородным смесям}}
{{\small
\begin{{center}}
\begin{{tabular}}{{@{{}}l l r r r r@{{}}}}
\toprule
Инструмент & Разнородность & Все, \% & Обяз., \% & \shortstack[r]{{\scriptsize В тройке лучших\\\scriptsize по {len(ucs_hetero)} разнор. сценариям}} & \shortstack[r]{{\scriptsize Среднее покрытие\\\scriptsize разнор. сценариев, \%}} \\
\midrule
{chr(10).join(het_cov_rows)}
\bottomrule
\end{{tabular}}
\end{{center}}}}
\begin{{itemize}}
\item Схему ECME среди разнородных средств реализует только {tts(ecme_hetero)}; блочную схему ECM --- {tts(ecm_hetero)}.
Остальные средства либо оптимизируют все параметры сразу (\texttt{{pomegranate}}, \texttt{{mixem}}), либо вообще не используют итерационное оценивание
(\texttt{{brms}} применяет байесовское сэмплирование).
\item Мультистарт, информационные критерии, фиксацию параметров и явные границы одновременно выполняет {tts(full_pack) if full_pack else 'ни одно средство'}.
Этот инструмент не оценивает смесь итерационно по максимуму правдоподобия.
\item Сравнение конфигураций семейств (\texttt{{STRUC-13}}) {'выполняет ' + tts(config_hetero) if config_hetero else 'не выполняет ни одно из этих средств'}; для разнородных смесей остаётся
комбинаторным перебором, который нужно ограничивать порядком и бюджетом.
\item Бутстреп отношения правдоподобий {'выполняет ' + tts(bootstrap_hetero) if bootstrap_hetero else 'не реализован ни в одном из этих средств'}.
\end{{itemize}}
"""
)

# ================================================================ ЧАСТЬ VI. MPEST
w(r"\part{Положение \texttt{pysatl-mpest}}")
gap_rows = []
for rid, stt, ycnt, ncrit, ndes in gaps:
    donors = [t for t in others if status[(t, rid)] == "yes"]
    gap_rows.append(
        rf"{T(rid)} & {esc(req[rid]['name'])} & {esc(PRIORITY_NAMES[req[rid]['priority']])} & {st(MPEST, rid)} & {ycnt} & {ncrit or '---'} & {ndes or '---'} & {', '.join(esc(tool_name[t]) for t in donors[:4]) or '---'} \\"
    )
w(r"\begin{landscape}")
w(
    rf"""\section{{Пробелы}}
\texttt{{{MPEST}}} выполняет полностью {tool_counts[MPEST]['yes']} из {len(reqs)} требований, частично --- {tool_counts[MPEST]['partial']}, не выполняет --- {tool_counts[MPEST]['no']}.
Покрытие: общее {pct(total_score[MPEST])}, обязательные {pct(mpest_must)}, желательные {pct(score(MPEST, should_ids))}, факультативные {pct(score(MPEST, could_ids))}.
Возможности, которые больше не выполняет полностью ни один инструмент: {'; '.join(rl(r) for r in only_mpest) or 'нет'}.

Таблица содержит все требования, не выполненные полностью, в порядке приоритета, числа сценариев с критическим требованием и числа сценариев с желательным.
<<Др.>> --- сколько других инструментов выполняют требование полностью; <<Доноры>> --- первые из них (готовые решения, которые можно изучить).
{{\scriptsize\setlength{{\tabcolsep}}{{3pt}}
\begin{{longtable}}{{@{{}}l >{{\raggedright\arraybackslash}}p{{8.2cm}} l l r r r >{{\raggedright\arraybackslash}}p{{6.2cm}}@{{}}}}
\toprule
ID & Требование & Приоритет & Статус & Др. & Крит. & Жел. & Доноры \\
\midrule
\endhead
{chr(10).join(gap_rows)}
\bottomrule
\end{{longtable}}}}
"""
)
w(r"\end{landscape}")

w(
    rf"""\section{{Приоритеты развития}}\label{{sec:roadmap}}
Чтобы упорядочить пробелы по пользе для прикладных задач, для каждого невыполненного требования рассчитан средний прирост покрытия критических требований по {len(ucs)} сценариям:
прирост равен сумме по сценариям, где требование критическое, величины (недостающая доля требования)/(число критических требований сценария), делённой на {len(ucs)}.
Таким образом, требование ценнее, если оно критично для многих сценариев с коротким списком критических требований. Расчёт не учитывает трудоёмкость реализации.

В таблице: <<Сцен.>> --- число сценариев с критическим требованием, <<Прирост>> --- вклад требования в среднее покрытие (процентные пункты), <<Накопл.>> --- среднее покрытие после закрытия этого и всех предыдущих пробелов (\%).

Исходное среднее покрытие критических требований по сценариям: {pct(base_mean)}. Если довести до полного выполнения все обязательные требования (в том числе выполненные частично), оно станет {pct(mpest_after_must[0])},
общее покрытие --- {pct(mpest_after_must[1])}; если закрыть все критические требования сценариев --- {pct(mpest_after_crit[0])}.
{{\footnotesize
\begin{{longtable}}{{@{{}}r l >{{\raggedright\arraybackslash}}p{{5.8cm}} l r r r@{{}}}}
\toprule
\# & ID & Требование & Приоритет & Сцен. & Прирост & Накопл. \\
\midrule
\endhead
{chr(10).join(rf"{i + 1} & {T(g[0])} & {esc(req[g[0]]['name'])} & {esc(PRIORITY_NAMES[req[g[0]]['priority']])} & {g[3]} & {gain[g[0]] * 100:.1f} & {curve[i][1] * 100:.1f} \\" for i, g in enumerate(gap_by_gain[:12]))}
\bottomrule
\end{{longtable}}}}
Первые двенадцать пробелов поднимают среднее покрытие с {pct(base_mean)} до {pct(curve[-1][1]) if curve else '---'}.
Порядок следует читать как ориентир: он основан на критичности для выбранных сценариев, а не на оценке стоимости разработки.

\section{{Что ещё следует из таблиц}}
\begin{{itemize}}
\item Обязательные требования, не выполненные \texttt{{{MPEST}}}: {'; '.join(rn(g[0]) for g in must_gaps) or 'нет'}. Для каждого из них в таблице пробелов указаны инструменты-доноры.
\item Критические требования не менее чем двух сценариев, выполненные не полностью: {'; '.join(rn(r) for r in crit_gaps)}.
\item Связь методов EM, ECM и ECME с объёмом данных и числом компонент в базе не оценивалась: сценарии различаются выборкой
({', '.join(esc(SAMPLE[k]) for k in dict.fromkeys(u['sample_regime'] for u in ucs))}) и знанием числа компонент, но оценки фиксируют наличие метода, а не его поведение.
Выбор метода под класс сценария проверяется экспериментально.
\end{{itemize}}
"""
)

w(r"\end{document}")

OUT.parent.mkdir(exist_ok=True)
OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
