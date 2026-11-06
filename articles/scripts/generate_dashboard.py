#!/usr/bin/env python3
"""
Interactive HTML Dashboard Generator for pysatl-mpest Master's Thesis.
Reads normalized CSVs from articles/raw/ and generates a standalone,
zero-dependency, responsive HTML dashboard with:
  1. Full summary matrix with green/yellow/red color palette.
  2. Category / requirement type filtering and presets.
  3. Interactive literature explorer per requirement with citations filtering,
     ranking, role filters, and DOI links.
  4. Evidence inspector (notes and repository code links).
  5. Live instant search, tool/ecosystem multi-selection, and export to Markdown/CSV.

Usage:
    python3 articles/scripts/generate_dashboard.py
    python3 articles/scripts/generate_dashboard.py --output articles/dashboard.html
"""

import argparse
import csv
import json
import sys
from pathlib import Path

CATEGORY_NAMES = {
    "estimation": "Оценивание параметров (estimation)",
    "structure": "Структура смеси и выбор K (structure)",
    "initialization": "Инициализация параметров (initialization)",
    "technical": "Архитектура и API (technical)",
    "infrastructure": "Инженерия качества и CI (infrastructure)",
    "visualization": "Визуализация и графики (visualization)",
    "representation": "Представление смеси и интерфейс (representation)",
    "performance": "Производительность и параллелизация (performance)",
    "diagnostics": "Статистическая диагностика и бенчмарки (diagnostics)",
    "proprietary": "Проприетарные возможности (proprietary)",
}


def load_dataset(data_dir: Path) -> dict:
    reqs_dir = data_dir / "reqs" if (data_dir / "reqs").is_dir() else data_dir

    tools_path = reqs_dir / "tools.csv" if (reqs_dir / "tools.csv").exists() else data_dir / "tools.csv"
    reqs_path = data_dir / "requirements.csv" if (data_dir / "requirements.csv").exists() else (reqs_dir / "requirements.csv" if (reqs_dir / "requirements.csv").exists() else data_dir.parent / "requirements.csv")
    evals_path = reqs_dir / "evaluations.csv" if (reqs_dir / "evaluations.csv").exists() else data_dir / "evaluations.csv"
    arts_path = data_dir / "articles.csv" if (data_dir / "articles.csv").exists() else (reqs_dir / "articles.csv" if (reqs_dir / "articles.csv").exists() else data_dir.parent / "articles.csv")
    req_arts_path = reqs_dir / "requirement_articles.csv" if (reqs_dir / "requirement_articles.csv").exists() else data_dir / "requirement_articles.csv"

    for p in [tools_path, reqs_path, evals_path, arts_path, req_arts_path]:
        if not p.exists():
            raise FileNotFoundError(f"Файл не найден: {p}")

    with open(tools_path, "r", encoding="utf-8") as f:
        tools = list(csv.DictReader(f))

    with open(reqs_path, "r", encoding="utf-8") as f:
        requirements = list(csv.DictReader(f))

    with open(evals_path, "r", encoding="utf-8") as f:
        evaluations = list(csv.DictReader(f))

    with open(arts_path, "r", encoding="utf-8") as f:
        articles = list(csv.DictReader(f))
        for a in articles:
            try:
                a["citations_count"] = int(a.get("citations_count", 0))
            except ValueError:
                a["citations_count"] = 0

    with open(req_arts_path, "r", encoding="utf-8") as f:
        requirement_articles = list(csv.DictReader(f))

    return {
        "tools": tools,
        "requirements": requirements,
        "evaluations": evaluations,
        "articles": articles,
        "requirement_articles": requirement_articles,
        "category_names": CATEGORY_NAMES,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PySATL mpest — Интерактивная матрица требований и навигатор литературы</title>
  <!-- Early Dark Mode Detection -->
  <script>
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  </script>
  <!-- Tailwind CSS via CDN with fallback styling -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            },
            statusYes: {
              bg: '#dcfce7',
              text: '#166534',
              border: '#86efac',
            },
            statusPartial: {
              bg: '#fef9c3',
              text: '#854d0e',
              border: '#fde047',
            },
            statusNo: {
              bg: '#fee2e2',
              text: '#991b1b',
              border: '#fca5a5',
            }
          }
        }
      }
    }
  </script>
  <style>
    .hidden {
      display: none !important;
    }
    /* Custom styling for matrix table and sticky elements */
    .table-container {
      max-height: calc(100vh - 270px);
      overflow: auto;
      scrollbar-width: thin;
    }
    .dark .table-container {
      scrollbar-color: #475569 #0f172a;
    }
    .dark .table-container::-webkit-scrollbar {
      background-color: #0f172a;
    }
    .dark .table-container::-webkit-scrollbar-thumb {
      background-color: #334155;
      border-radius: 4px;
    }
    .dark .table-container::-webkit-scrollbar-thumb:hover {
      background-color: #475569;
    }
    .sticky-th {
      position: sticky;
      top: 0;
      z-index: 20;
    }
    .sticky-col-1 {
      position: sticky;
      left: 0;
      z-index: 10;
    }
    .sticky-col-2 {
      position: sticky;
      left: 72px;
      z-index: 10;
    }
    .sticky-col-target {
      position: sticky;
      left: 312px;
      z-index: 10;
    }
    .sticky-header-corner-1 {
      position: sticky;
      left: 0;
      top: 0;
      z-index: 30;
    }
    .sticky-header-corner-2 {
      position: sticky;
      left: 72px;
      top: 0;
      z-index: 30;
    }
    .sticky-header-corner-target {
      position: sticky;
      left: 312px;
      top: 0;
      z-index: 30;
    }
    /* Cell status badge styles */
    .status-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 3px 8px;
      font-size: 11px;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      user-select: none;
    }
    .status-badge:hover {
      filter: brightness(0.92);
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .status-yes {
      background-color: #dcfce7;
      color: #166534;
      border: 1px solid #86efac;
    }
    .status-partial {
      background-color: #fef9c3;
      color: #854d0e;
      border: 1px solid #fde047;
    }
    .status-no {
      background-color: #fee2e2;
      color: #991b1b;
      border: 1px solid #fca5a5;
    }
    .priority-must { background-color: #fecdd3; color: #9f1239; }
    .priority-should { background-color: #fed7aa; color: #9a3412; }
    .priority-could { background-color: #e2e8f0; color: #475569; }

    /* Dark mode badge overrides */
    .dark .status-yes {
      background-color: #064e3b;
      color: #6ee7b7;
      border: 1px solid #047857;
    }
    .dark .status-partial {
      background-color: #713f12;
      color: #fde047;
      border: 1px solid #a16207;
    }
    .dark .status-no {
      background-color: #7f1d1d;
      color: #fca5a5;
      border: 1px solid #b91c1c;
    }
    .dark .priority-must { background-color: #881337; color: #fecdd3; }
    .dark .priority-should { background-color: #7c2d12; color: #fed7aa; }
    .dark .priority-could { background-color: #334155; color: #cbd5e1; }

    /* Modal slide-in */
    .drawer {
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
  </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 antialiased min-h-screen flex flex-col font-sans transition-colors duration-200">

  <!-- Header -->
  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40 shadow-sm transition-colors duration-200">
    <div class="max-w-[1920px] mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow">
          Ψ
        </div>
        <div>
          <h1 class="text-lg font-bold text-slate-900 dark:text-slate-100 leading-tight flex items-center gap-2">
            PySATL mpest — Навигатор требований и доказательной литературы
            <span class="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300">ВКР 2026</span>
            <span id="build-timestamp-badge" class="text-[11px] font-medium px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">__BUILD_TIMESTAMP__</span>
          </h1>
          <p id="header-subtitle" class="text-xs text-slate-500 dark:text-slate-400">
            Сравнительный анализ __NUM_TOOLS__ открытых пакетов (Python, R, Julia, C++), __NUM_REQS__ требований и __NUM_ARTICLES__ рецензируемых публикаций
          </p>
        </div>
      </div>

      <!-- Quick Metrics & Actions -->
      <div class="flex items-center flex-wrap gap-2 text-xs">
        <a href="usecases_dashboard.html" class="px-3 py-1.5 bg-indigo-50 dark:bg-indigo-950/70 hover:bg-indigo-100 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-semibold rounded-lg border border-indigo-200 dark:border-indigo-800 shadow-sm transition flex items-center gap-1.5" title="Перейти к прикладным юзкейсам">
          <span>🎯</span> Прикладные сценарии и бенчмарки →
        </a>
        <div class="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
          <span class="text-slate-500 dark:text-slate-400">Показано:</span>
          <span id="metric-reqs" class="font-bold text-slate-900 dark:text-slate-100">__NUM_REQS__ требований</span>
          <span class="text-slate-300 dark:text-slate-600">|</span>
          <span id="metric-tools" class="font-bold text-slate-900 dark:text-slate-100">__NUM_TOOLS__ пакетов</span>
        </div>
        <button id="btn-theme-toggle" class="px-2.5 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-medium rounded-lg border border-slate-300 dark:border-slate-700 shadow-sm transition flex items-center gap-1.5" title="Переключить тему оформления">
          <span id="theme-toggle-icon">🌙</span> <span id="theme-toggle-text">Темная</span>
        </button>
        <button id="btn-export-markdown" class="px-3 py-1.5 bg-slate-800 dark:bg-indigo-600 hover:bg-slate-900 dark:hover:bg-indigo-700 text-white font-medium rounded-lg shadow-sm transition flex items-center gap-1.5">
          <span>📋</span> Скопировать Markdown
        </button>
        <button id="btn-export-csv" class="px-3 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-medium rounded-lg border border-slate-300 dark:border-slate-700 shadow-sm transition flex items-center gap-1.5">
          <span>📊</span> Экспорт CSV
        </button>
        <button id="btn-help" class="px-2.5 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium rounded-lg border border-slate-300 dark:border-slate-700 shadow-sm transition">
          ❓ Легенда
        </button>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="bg-slate-50 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 px-4 py-2.5">
      <div class="max-w-[1920px] mx-auto flex flex-wrap items-center justify-between gap-3">
        <!-- Left: Search and Categories -->
        <div class="flex flex-wrap items-center gap-2 flex-grow">
          <!-- Live search -->
          <div class="relative w-72">
            <input type="text" id="input-search" placeholder="Поиск (код, фича, статья, автор)..."
                   class="w-full pl-8 pr-3 py-1.5 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 shadow-sm">
            <span class="absolute left-2.5 top-2 text-slate-400 dark:text-slate-500 text-xs">🔍</span>
          </div>

          <!-- Type filter dropdown -->
          <select id="select-category" class="py-1.5 px-3 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm font-medium">
            <option value="all">Все категории (__NUM_REQS__)</option>
            <!-- Generated dynamically -->
          </select>

          <!-- Ecosystem filter -->
          <div class="flex items-center bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-0.5 shadow-sm text-xs" id="eco-tabs">
            <button data-eco="all" class="eco-btn px-2.5 py-1 rounded font-medium text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/70">Все пакеты (__NUM_TOOLS__)</button>
            <button data-eco="python" class="eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white">Python (__NUM_PYTHON__)</button>
            <button data-eco="r" class="eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white">R (__NUM_R__)</button>
            <button data-eco="julia_cpp" class="eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white">Julia / C++ (__NUM_JULIA_CPP__)</button>
          </div>

          <!-- Preset filters -->
          <select id="select-preset" class="py-1.5 px-3 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm font-medium">
            <option value="all">⚡ Пресет: Все требования</option>
            <option value="mpest-killer">🎯 Киллер-фичи pysatl-mpest (mpest=Есть, аналоги=Нет/Частично)</option>
            <option value="mpest-backlog">⚠️ Бэклог pysatl-mpest (Must/Should со статусом Частично/Нет)</option>
            <option value="priority-must">🔥 Только Must-have требования</option>
            <option value="cited-high">📚 Высокоцитируемые темы (≥1 000 цитат)</option>
          </select>
        </div>

        <!-- Right: Tool selector modal button & reset -->
        <div class="flex items-center gap-2">
          <button id="btn-custom-tools" class="px-2.5 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium rounded-lg border border-slate-300 dark:border-slate-700 shadow-sm transition flex items-center gap-1">
            <span>⚙️</span> Выбрать пакеты (<span id="selected-tools-count">__NUM_TOOLS__</span>)
          </button>
          <button id="btn-reset-filters" class="px-2.5 py-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 font-medium transition">
            Сброс фильтров
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Matrix Container -->
  <main class="flex-grow max-w-[1920px] w-full mx-auto p-4">
    <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors duration-200">
      <div class="table-container">
        <table id="matrix-table" class="w-full text-left border-collapse text-xs">
          <thead>
            <tr id="matrix-header-row" class="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-800 font-semibold select-none">
              <!-- Dynamically populated -->
            </tr>
          </thead>
          <tbody id="matrix-body" class="divide-y divide-slate-100 dark:divide-slate-800">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>

      <!-- Footer / Status bar inside table container -->
      <div class="px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span>Клик по статусу — обоснование и строка кода.</span>
          <span>Клик по <span class="font-bold text-indigo-600 dark:text-indigo-400">📚 N</span> — полный список статей с фильтрами цитирования.</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span> Есть (yes)</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block"></span> Частично (partial)</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span> Нет (no)</span>
        </div>
      </div>
    </div>
  </main>

  <!-- DRAWER: Literature Explorer per Requirement -->
  <div id="drawer-literature" class="hidden fixed inset-0 z-50 overflow-hidden transition-opacity duration-200">
    <!-- Backdrop -->
    <div id="drawer-backdrop" class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"></div>

    <div class="absolute inset-y-0 right-0 pl-10 max-w-full flex">
      <div class="drawer w-screen max-w-2xl bg-white dark:bg-slate-900 shadow-2xl flex flex-col h-full border-l border-slate-200 dark:border-slate-800 transform translate-x-full">
        <!-- Drawer Header -->
        <div class="px-6 py-4 bg-slate-900 dark:bg-slate-950 text-white flex items-center justify-between border-b border-slate-800">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span id="lit-req-id" class="px-2 py-0.5 rounded bg-indigo-500 text-white text-xs font-mono font-bold">EST-01</span>
              <span id="lit-req-priority" class="px-2 py-0.5 rounded text-xs font-semibold uppercase">must</span>
              <span id="lit-req-type" class="text-xs text-slate-300">Оценивание</span>
            </div>
            <h2 id="lit-req-name" class="text-base font-bold text-white leading-tight">Классический EM-алгоритм</h2>
          </div>
          <button id="btn-close-drawer" class="text-slate-400 hover:text-white text-xl p-1 font-bold">✕</button>
        </div>

        <!-- Description Note -->
        <div class="px-6 py-3 bg-indigo-50/50 dark:bg-indigo-950/40 border-b border-indigo-100 dark:border-indigo-900/60 text-xs text-slate-700 dark:text-slate-300">
          <p id="lit-req-desc" class="italic leading-relaxed"></p>
        </div>

        <!-- Literature Filter Bar -->
        <div class="px-6 py-3 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <!-- Search in articles -->
          <div class="w-48">
            <input type="text" id="lit-filter-text" placeholder="Поиск в статьях..."
                   class="w-full px-2.5 py-1 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 rounded focus:ring-1 focus:ring-indigo-500">
          </div>

          <!-- Min Citations Filter -->
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500 dark:text-slate-400">Мин. цитат:</span>
            <select id="lit-filter-citations" class="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-medium">
              <option value="0">Все (≥ 0)</option>
              <option value="20">≥ 20</option>
              <option value="50">≥ 50</option>
              <option value="100">≥ 100</option>
              <option value="500">≥ 500</option>
              <option value="1000">≥ 1 000 (Классика)</option>
            </select>
          </div>

          <!-- Role Filter -->
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500 dark:text-slate-400">Роль:</span>
            <select id="lit-filter-role" class="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-medium">
              <option value="all">Все роли</option>
              <option value="foundation">Базис (foundation)</option>
              <option value="method">Метод (method)</option>
              <option value="benchmark">Бенчмарк (benchmark)</option>
            </select>
          </div>

          <!-- Sort -->
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500 dark:text-slate-400">Сортировка:</span>
            <select id="lit-filter-sort" class="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-medium">
              <option value="citations-desc">Цитаты ↓</option>
              <option value="year-desc">Год: новые ↓</option>
              <option value="year-asc">Год: старые ↑</option>
            </select>
          </div>

          <!-- Limit -->
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500 dark:text-slate-400">Лимит:</span>
            <select id="lit-filter-limit" class="border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-medium">
              <option value="5">Топ 5</option>
              <option value="10" selected>Топ 10</option>
              <option value="25">Топ 25</option>
              <option value="all">Все статьи</option>
            </select>
          </div>
        </div>

        <!-- Action / Export bar for articles -->
        <div class="px-6 py-2 bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
          <div class="text-slate-600 dark:text-slate-400 font-medium">
            Найдено статей: <span id="lit-matched-count" class="font-bold text-indigo-700 dark:text-indigo-400">0</span> из <span id="lit-total-count" class="font-bold text-slate-900 dark:text-slate-100">0</span>
          </div>
          <div class="flex items-center gap-2">
            <button id="btn-copy-lit-markdown" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium flex items-center gap-1">
              <span>📋</span> Копировать список (Markdown)
            </button>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <button id="btn-copy-lit-bibtex" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium flex items-center gap-1">
              <span>📚</span> BibTeX
            </button>
          </div>
        </div>

        <!-- Articles Cards List -->
        <div id="lit-articles-list" class="flex-grow overflow-y-auto p-6 space-y-3 divide-y divide-slate-100 dark:divide-slate-800">
          <!-- Dynamically populated -->
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Evidence Inspector -->
  <div id="modal-evidence" class="fixed inset-0 z-50 overflow-y-auto hidden">
    <div class="min-h-screen px-4 text-center flex items-center justify-center">
      <div id="modal-evidence-backdrop" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"></div>
      <div class="inline-block bg-white dark:bg-slate-900 rounded-xl text-left overflow-hidden shadow-2xl transform transition-all my-8 max-w-lg w-full z-10 p-6 border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4">
          <div>
            <div id="ev-tool-name" class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Инструмент</div>
            <h3 id="ev-title" class="text-base font-bold text-slate-900 dark:text-slate-100">Оценка функционального требования</h3>
          </div>
          <button id="btn-close-evidence" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg font-bold">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div>
            <span class="text-slate-500 dark:text-slate-400 block mb-1">Описание требования:</span>
            <div id="ev-req-desc" class="p-3 bg-slate-50 dark:bg-slate-800/70 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 leading-relaxed font-sans"></div>
          </div>

          <div>
            <span class="text-slate-500 dark:text-slate-400 block mb-1">Статус поддержки:</span>
            <div id="ev-status-badge"></div>
          </div>

          <div>
            <span class="text-slate-500 dark:text-slate-400 block mb-1">Обоснование и специфика реализации:</span>
            <div id="ev-note" class="p-3 bg-slate-50 dark:bg-slate-800/70 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 leading-relaxed font-sans"></div>
          </div>

          <div>
            <span class="text-slate-500 dark:text-slate-400 block mb-1">Доказательная ссылка / место в коде:</span>
            <div id="ev-link-container"></div>
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button id="btn-close-evidence-ok" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-medium transition shadow-sm">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Custom Tool Selector -->
  <div id="modal-tools" class="fixed inset-0 z-50 overflow-y-auto hidden">
    <div class="min-h-screen px-4 text-center flex items-center justify-center">
      <div id="modal-tools-backdrop" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"></div>
      <div class="inline-block bg-white dark:bg-slate-900 rounded-xl text-left overflow-hidden shadow-2xl transform transition-all my-8 max-w-2xl w-full z-10 p-6 border border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4">
          <div>
            <h3 class="text-base font-bold text-slate-900 dark:text-slate-100">Выбор отображаемых инструментов</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Выберите интересующие пакеты для прямого сравнения без лишних колонок</p>
          </div>
          <button id="btn-close-tools" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg font-bold">✕</button>
        </div>

        <div class="flex items-center justify-between mb-3 text-xs">
          <div class="space-x-2">
            <button id="btn-select-all-tools" class="text-indigo-600 dark:text-indigo-400 hover:underline font-medium">Выбрать все (__NUM_TOOLS__)</button>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <button id="btn-select-only-mpest" class="text-indigo-600 dark:text-indigo-400 hover:underline font-medium">Только mpest</button>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <button id="btn-select-python-tools" class="text-indigo-600 dark:text-indigo-400 hover:underline font-medium">Все Python (__NUM_PYTHON__)</button>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <button id="btn-select-r-tools" class="text-indigo-600 dark:text-indigo-400 hover:underline font-medium">Все R (__NUM_R__)</button>
          </div>
        </div>

        <div id="tools-checkbox-grid" class="max-h-96 overflow-y-auto grid grid-cols-2 sm:grid-cols-3 gap-2.5 p-2 bg-slate-50 dark:bg-slate-950/60 rounded-lg border border-slate-200 dark:border-slate-800 text-xs">
          <!-- Dynamically populated -->
        </div>

        <div class="mt-6 flex justify-end gap-2 text-xs">
          <button id="btn-apply-tools" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition shadow-sm">
            Применить
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Legend & Help -->
  <div id="modal-help" class="fixed inset-0 z-50 overflow-y-auto hidden">
    <div class="min-h-screen px-4 text-center flex items-center justify-center">
      <div id="modal-help-backdrop" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"></div>
      <div class="inline-block bg-white dark:bg-slate-900 rounded-xl text-left overflow-hidden shadow-2xl transform transition-all my-8 max-w-xl w-full z-10 p-6 border border-slate-200 dark:border-slate-800 text-xs">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4">
          <h3 class="text-base font-bold text-slate-900 dark:text-slate-100">Справочник и цветовая шкала матрицы</h3>
          <button id="btn-close-help" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg font-bold">✕</button>
        </div>

        <div class="space-y-4 text-slate-700 dark:text-slate-300">
          <div>
            <h4 class="font-bold text-slate-900 dark:text-slate-100 mb-1.5">Цветовая шкала статусов поддержки:</h4>
            <div class="space-y-1.5">
              <div class="flex items-center gap-2">
                <span class="status-badge status-yes">✓ Есть</span>
                <span>Возможность полностью реализована в публичном API и подтверждена кодом или тестами.</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="status-badge status-partial">~ Частично</span>
                <span>Реализована для ограниченного подмножества случаев (например, только для 1D или без аналитического M-шага).</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="status-badge status-no">✗ Нет</span>
                <span>Возможность отсутствует или требует внешней ручной обвязки пользователем.</span>
              </div>
            </div>
          </div>

          <div>
            <h4 class="font-bold text-slate-900 dark:text-slate-100 mb-1.5">Приоритеты требований:</h4>
            <div class="space-y-1">
              <div><span class="px-2 py-0.5 rounded text-xs font-semibold uppercase priority-must">must</span> — критически необходимо для базового релиза библиотеки.</div>
              <div><span class="px-2 py-0.5 rounded text-xs font-semibold uppercase priority-should">should</span> — важное конкурентное преимущество, запланированное к выпуску.</div>
              <div><span class="px-2 py-0.5 rounded text-xs font-semibold uppercase priority-could">could</span> — факультативное расширение или нишевый алгоритм.</div>
            </div>
          </div>

          <div>
            <h4 class="font-bold text-slate-900 dark:text-slate-100 mb-1.5">Наукометрическая доказательная база:</h4>
            <p class="leading-relaxed">
              Колонка <b>«Статьи (N)»</b> отображает число рецензируемых публикаций, в которых данное требование исследовано математически или реализовано. Клик по кнопке открывает перечень статей с сортировкой по цитируемости и фильтрами.
            </p>
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button id="btn-close-help-ok" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition shadow-sm">
            Понятно
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 px-4 py-2 rounded-lg text-xs font-medium shadow-lg transform translate-y-20 opacity-0 transition-all duration-300 pointer-events-none">
    Уведомление
  </div>

  <!-- Embedded Dataset -->
  <script id="matrix-data" type="application/json">
__RAW_JSON_DATA__
  </script>

  <!-- Application Logic -->
  <script>
    (function() {
      // 1. Parse dataset
      const rawData = JSON.parse(document.getElementById('matrix-data').textContent);
      const { tools, requirements, evaluations, articles, requirement_articles, category_names } = rawData;

      // Indexing
      const toolMap = new Map(tools.map(t => [t.tool_id, t]));
      const reqMap = new Map(requirements.map(r => [r.req_id, r]));
      const articleMap = new Map(articles.map(a => [a.article_id, a]));

      // Evaluations lookup: (tool_id + '::' + req_id) -> eval
      const evalMap = new Map();
      evaluations.forEach(e => {
        evalMap.set(`${e.tool_id}::${e.req_id}`, e);
      });

      // Requirement to articles lookup: req_id -> [ { article, role, context_note } ]
      const reqArticlesMap = new Map();
      requirement_articles.forEach(ra => {
        const art = articleMap.get(ra.article_id);
        if (art) {
          if (!reqArticlesMap.has(ra.req_id)) reqArticlesMap.set(ra.req_id, []);
          reqArticlesMap.get(ra.req_id).push({
            article: art,
            role: ra.role || 'method',
            context_note: ra.context_note || ''
          });
        }
      });

      // Sort articles within each requirement by citation count desc by default
      reqArticlesMap.forEach((list) => {
        list.sort((a, b) => (b.article.citations_count || 0) - (a.article.citations_count || 0));
      });

      // Ecosystem mapping
      const ECOSYSTEM_TOOL_IDS = {
        python: tools.filter(t => t.ecosystem === 'Python').map(t => t.tool_id),
        r: tools.filter(t => t.ecosystem.includes('R')).map(t => t.tool_id),
        julia_cpp: tools.filter(t => !t.ecosystem.includes('R') && (t.ecosystem.includes('Julia') || t.ecosystem.includes('C++'))).map(t => t.tool_id)
      };

      // State
      let selectedToolIds = tools.map(t => t.tool_id);
      // Ensure pysatl-mpest is always first
      if (selectedToolIds.includes('pysatl-mpest')) {
        selectedToolIds = ['pysatl-mpest', ...selectedToolIds.filter(id => id !== 'pysatl-mpest')];
      }

      let currentCategory = 'all';
      let currentPreset = 'all';
      let currentEco = 'all';
      let searchQuery = '';

      // Active requirement in drawer
      let activeReqForDrawer = null;

      // DOM Elements
      const tableHead = document.getElementById('matrix-header-row');
      const tableBody = document.getElementById('matrix-body');
      const inputSearch = document.getElementById('input-search');
      const selectCategory = document.getElementById('select-category');
      const selectPreset = document.getElementById('select-preset');
      const ecoTabs = document.getElementById('eco-tabs');
      const metricReqs = document.getElementById('metric-reqs');
      const metricTools = document.getElementById('metric-tools');
      const selectedToolsCount = document.getElementById('selected-tools-count');

      // Modals and Drawers
      const drawerLit = document.getElementById('drawer-literature');
      const modalEvidence = document.getElementById('modal-evidence');
      const modalTools = document.getElementById('modal-tools');
      const modalHelp = document.getElementById('modal-help');
      const toast = document.getElementById('toast');

      // Dynamic sync for header subtitle, all categories, eco buttons and modals
      const headerSubtitle = document.getElementById('header-subtitle');
      if (headerSubtitle) {
        headerSubtitle.textContent = `Сравнительный анализ ${tools.length} открытых пакетов (Python, R, Julia, C++), ${requirements.length} требований и ${articles.length} рецензируемых публикаций`;
      }
      if (selectCategory && selectCategory.options.length > 0) {
        selectCategory.options[0].textContent = `Все категории (${requirements.length})`;
      }
      const ecoBtnAll = document.querySelector('[data-eco="all"]');
      if (ecoBtnAll) ecoBtnAll.textContent = `Все пакеты (${tools.length})`;
      const ecoBtnPy = document.querySelector('[data-eco="python"]');
      if (ecoBtnPy) ecoBtnPy.textContent = `Python (${ECOSYSTEM_TOOL_IDS.python.length})`;
      const ecoBtnR = document.querySelector('[data-eco="r"]');
      if (ecoBtnR) ecoBtnR.textContent = `R (${ECOSYSTEM_TOOL_IDS.r.length})`;
      const ecoBtnJC = document.querySelector('[data-eco="julia_cpp"]');
      if (ecoBtnJC) ecoBtnJC.textContent = `Julia / C++ (${ECOSYSTEM_TOOL_IDS.julia_cpp.length})`;
      const btnSelectAllTools = document.getElementById('btn-select-all-tools');
      if (btnSelectAllTools) btnSelectAllTools.textContent = `Выбрать все (${tools.length})`;
      const btnSelectPyTools = document.getElementById('btn-select-python-tools');
      if (btnSelectPyTools) btnSelectPyTools.textContent = `Все Python (${ECOSYSTEM_TOOL_IDS.python.length})`;
      const btnSelectRTools = document.getElementById('btn-select-r-tools');
      if (btnSelectRTools) btnSelectRTools.textContent = `Все R (${ECOSYSTEM_TOOL_IDS.r.length})`;

      // Populate Category Filter dropdown
      Object.keys(category_names).forEach(catKey => {
        const opt = document.createElement('option');
        opt.value = catKey;
        const count = requirements.filter(r => r.type === catKey).length;
        opt.textContent = `${category_names[catKey]} (${count})`;
        selectCategory.appendChild(opt);
      });

      // Populate Custom Tools Checkboxes in Modal
      const toolsGrid = document.getElementById('tools-checkbox-grid');
      tools.forEach(t => {
        const label = document.createElement('label');
        label.className = 'flex items-center gap-2 p-2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 cursor-pointer select-none';
        label.innerHTML = `
          <input type="checkbox" value="${t.tool_id}" class="tool-checkbox rounded text-indigo-600 focus:ring-indigo-500" ${selectedToolIds.includes(t.tool_id) ? 'checked' : ''}>
          <div class="truncate">
            <span class="font-bold text-slate-800 dark:text-slate-200">${t.tool_id}</span>
            <span class="text-[10px] text-slate-400 dark:text-slate-500 block">${t.ecosystem}</span>
          </div>
        `;
        toolsGrid.appendChild(label);
      });

      // Toast Notification Helper
      function showToast(msg) {
        toast.textContent = msg;
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => {
          toast.classList.add('translate-y-20', 'opacity-0');
        }, 2200);
      }

      // Filter requirements
      function getFilteredRequirements() {
        return requirements.filter(req => {
          // Category filter
          if (currentCategory !== 'all' && req.type !== currentCategory) return false;

          // Preset filter
          if (currentPreset === 'priority-must' && req.priority !== 'must') return false;
          if (currentPreset === 'cited-high') {
            const arts = reqArticlesMap.get(req.req_id) || [];
            const maxCit = arts.reduce((max, a) => Math.max(max, a.article.citations_count || 0), 0);
            if (maxCit < 1000) return false;
          }
          if (currentPreset === 'mpest-killer') {
            const mpestEval = evalMap.get(`pysatl-mpest::${req.req_id}`);
            if (!mpestEval || mpestEval.status !== 'yes') return false;
            // Check competitors: at least 70% of others are 'no' or 'partial'
            let othersYes = 0;
            let totalOthers = 0;
            tools.forEach(t => {
              if (t.tool_id !== 'pysatl-mpest') {
                totalOthers++;
                const ev = evalMap.get(`${t.tool_id}::${req.req_id}`);
                if (ev && ev.status === 'yes') othersYes++;
              }
            });
            if (othersYes > 4) return false; // Not a killer feature if too many others also have it
          }
          if (currentPreset === 'mpest-backlog') {
            if (req.priority === 'could') return false;
            const mpestEval = evalMap.get(`pysatl-mpest::${req.req_id}`);
            if (mpestEval && mpestEval.status === 'yes') return false;
          }

          // Search query filter
          if (searchQuery) {
            const q = searchQuery.toLowerCase();
            const arts = reqArticlesMap.get(req.req_id) || [];
            const matchInReq = req.req_id.toLowerCase().includes(q) ||
                               req.name.toLowerCase().includes(q) ||
                               req.description.toLowerCase().includes(q);
            if (matchInReq) return true;

            const matchInArticles = arts.some(a =>
              a.article.title.toLowerCase().includes(q) ||
              a.article.authors.toLowerCase().includes(q) ||
              a.context_note.toLowerCase().includes(q)
            );
            if (matchInArticles) return true;

            return false;
          }

          return true;
        });
      }

      // Format Author Short
      function formatAuthorShort(authors) {
        if (!authors || authors === 'None') return 'Unknown';
        const first = authors.split(/[;,]/)[0].trim();
        const parts = first.split(/\s+/);
        const surname = parts[parts.length - 1];
        if (authors.includes(';') || authors.includes(',') || authors.toLowerCase().includes(' and ')) {
          return `${surname} et al.`;
        }
        return surname;
      }

      // Render Matrix Header
      function renderHeader() {
        let html = `
          <th class="sticky-header-corner-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 p-2.5 w-16 text-center border-r border-slate-200 dark:border-slate-700">Код</th>
          <th class="sticky-header-corner-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 p-2.5 w-60 border-r border-slate-200 dark:border-slate-700">Требование / Возможность</th>
        `;

        selectedToolIds.forEach(tId => {
          const tool = toolMap.get(tId);
          const isTarget = tId === 'pysatl-mpest';
          const headerClass = isTarget
            ? 'sticky-header-corner-target bg-indigo-50 dark:bg-indigo-950/80 border-r-2 border-indigo-300 dark:border-indigo-600 text-indigo-900 dark:text-indigo-200 font-bold px-2 py-2 text-center min-w-[110px]'
            : 'sticky-th bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-r border-slate-200 dark:border-slate-700 px-2 py-2 text-center min-w-[95px] max-w-[120px] truncate';

          html += `
            <th class="${headerClass}" title="${tool ? tool.name + ' (' + tool.ecosystem + ')' : tId}">
              <div class="truncate text-xs">${tool ? tool.name : tId}</div>
              <div class="text-[10px] font-normal text-slate-400 dark:text-slate-500">${tool ? tool.ecosystem : ''}</div>
            </th>
          `;
        });

        html += `
          <th class="sticky-th bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 p-2.5 text-center w-24 border-r border-slate-200 dark:border-slate-700">Статьи (N)</th>
          <th class="sticky-th bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 p-2.5 min-w-[240px]">Ключевые публикации (цитирования)</th>
        `;

        tableHead.innerHTML = html;
      }

      // Render Table Rows
      function renderMatrix() {
        renderHeader();
        const filteredReqs = getFilteredRequirements();

        metricReqs.textContent = `${filteredReqs.length} требований`;
        metricTools.textContent = `${selectedToolIds.length} пакетов`;
        selectedToolsCount.textContent = selectedToolIds.length;

        if (filteredReqs.length === 0) {
          tableBody.innerHTML = `
            <tr>
              <td colspan="${selectedToolIds.length + 4}" class="p-8 text-center text-slate-400 dark:text-slate-500">
                По заданным критериям фильтрации требований не найдено.
              </td>
            </tr>
          `;
          return;
        }

        // Group requirements by type
        const reqsByType = new Map();
        filteredReqs.forEach(r => {
          if (!reqsByType.has(r.type)) reqsByType.set(r.type, []);
          reqsByType.get(r.type).push(r);
        });

        let bodyHtml = '';

        reqsByType.forEach((typeReqs, typeKey) => {
          const typeTitle = category_names[typeKey] || typeKey;
          bodyHtml += `
            <tr class="bg-slate-200/60 dark:bg-slate-800/80 font-semibold text-slate-700 dark:text-slate-200 text-xs select-none">
              <td colspan="${selectedToolIds.length + 4}" class="px-3 py-1.5 border-y border-slate-300 dark:border-slate-700">
                📁 ${typeTitle} <span class="text-slate-500 dark:text-slate-400 font-normal">(${typeReqs.length})</span>
              </td>
            </tr>
          `;

          typeReqs.forEach(req => {
            const articles = reqArticlesMap.get(req.req_id) || [];
            const nArticles = articles.length;

            const prioBadge = `priority-${req.priority}`;

            bodyHtml += `<tr class="hover:bg-indigo-50/20 dark:hover:bg-slate-800/50 transition-colors group">`;

            // Col 1: Code
            bodyHtml += `
              <td class="sticky-col-1 bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800 p-2 font-mono font-bold text-slate-700 dark:text-slate-300 border-r border-slate-200 dark:border-slate-800 text-center">
                ${req.req_id}
              </td>
            `;

            // Col 2: Name & priority
            bodyHtml += `
              <td class="sticky-col-2 bg-white dark:bg-slate-900 group-hover:bg-slate-50 dark:group-hover:bg-slate-800 p-2 border-r border-slate-200 dark:border-slate-800 max-w-[240px]">
                <div class="flex items-center gap-1.5 mb-0.5">
                  <span class="font-semibold text-slate-900 dark:text-slate-100 leading-snug">${req.name}</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="px-1.5 py-0.2 rounded text-[10px] font-semibold uppercase ${prioBadge}">${req.priority}</span>
                  <span class="text-[10px] text-slate-400 dark:text-slate-400 truncate max-w-[180px]" title="${req.description}">${req.description}</span>
                </div>
              </td>
            `;

            // Tool Status Columns
            selectedToolIds.forEach(tId => {
              const isTarget = tId === 'pysatl-mpest';
              const ev = evalMap.get(`${tId}::${req.req_id}`);
              const status = ev ? ev.status.toLowerCase() : 'no';

              let badgeText = '✗ Нет';
              let badgeClass = 'status-no';
              if (status === 'yes') {
                badgeText = '✓ Есть';
                badgeClass = 'status-yes';
              } else if (status === 'partial') {
                badgeText = '~ Частично';
                badgeClass = 'status-partial';
              }

              const cellBgClass = isTarget
                ? 'sticky-col-target bg-indigo-50/50 dark:bg-indigo-950/40 group-hover:bg-indigo-100/50 dark:group-hover:bg-indigo-900/50 border-r-2 border-indigo-300 dark:border-indigo-700'
                : 'border-r border-slate-200 dark:border-slate-800';

              bodyHtml += `
                <td class="${cellBgClass} p-1.5 text-center">
                  <span class="status-badge ${badgeClass}"
                        data-tool-id="${tId}"
                        data-req-id="${req.req_id}">
                    ${badgeText}
                  </span>
                </td>
              `;
            });

            // Col: Articles count (clickable)
            bodyHtml += `
              <td class="p-1.5 text-center border-r border-slate-200 dark:border-slate-800">
                <button class="btn-open-lit inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-slate-700 dark:text-slate-300 hover:text-indigo-800 dark:hover:text-indigo-200 font-semibold text-xs border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500 transition"
                        data-req-id="${req.req_id}">
                  <span>📚</span> ${nArticles}
                </button>
              </td>
            `;

            // Col: Key articles compact preview
            const topArticles = articles.slice(0, 2);
            let topArticlesHtml = '—';
            if (topArticles.length > 0) {
              const previewItems = topArticles.map(a => {
                const author = formatAuthorShort(a.article.authors);
                const yr = a.article.year;
                const cit = a.article.citations_count;
                const citStr = cit >= 1000 ? (cit / 1000).toFixed(1) + 'k' : cit;
                const doi = a.article.doi || a.article.url;
                const link = (doi && doi.startsWith('http')) ? doi : '#';
                return `<a href="${link}" target="_blank" class="hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline">${author} (${yr}, <b>${citStr}</b>)</a>`;
              });
              topArticlesHtml = previewItems.join(', ');
              if (nArticles > 2) {
                topArticlesHtml += `, <span class="text-slate-400 dark:text-slate-500 italic cursor-pointer btn-open-lit" data-req-id="${req.req_id}">+${nArticles - 2} еще</span>`;
              }
            }

            bodyHtml += `
              <td class="p-2 text-slate-600 dark:text-slate-400 text-xs">
                ${topArticlesHtml}
              </td>
            `;

            bodyHtml += `</tr>`;
          });
        });

        tableBody.innerHTML = bodyHtml;

        // Attach event listeners to status badges
        document.querySelectorAll('.status-badge').forEach(badge => {
          badge.addEventListener('click', () => {
            const toolId = badge.getAttribute('data-tool-id');
            const reqId = badge.getAttribute('data-req-id');
            openEvidenceModal(toolId, reqId);
          });
        });

        // Attach event listeners to literature buttons
        document.querySelectorAll('.btn-open-lit').forEach(btn => {
          btn.addEventListener('click', () => {
            const reqId = btn.getAttribute('data-req-id');
            openLiteratureDrawer(reqId);
          });
        });
      }

      // -----------------------------------------------------------
      // Evidence Inspector Modal
      // -----------------------------------------------------------
      function openEvidenceModal(toolId, reqId) {
        const tool = toolMap.get(toolId);
        const req = reqMap.get(reqId);
        const ev = evalMap.get(`${toolId}::${reqId}`);

        document.getElementById('ev-tool-name').textContent = `${tool ? tool.name : toolId} (${tool ? tool.ecosystem : ''})`;
        document.getElementById('ev-title').textContent = `${reqId}: ${req ? req.name : ''}`;

        const reqDescContainer = document.getElementById('ev-req-desc');
        if (reqDescContainer) {
          reqDescContainer.textContent = req && req.description ? req.description : 'Описание требования отсутствует.';
        }

        const statusBadgeContainer = document.getElementById('ev-status-badge');
        const noteContainer = document.getElementById('ev-note');
        const linkContainer = document.getElementById('ev-link-container');

        const status = ev ? ev.status.toLowerCase() : 'no';
        let statusBadge = '<span class="status-badge status-no">✗ Нет</span>';
        if (status === 'yes') statusBadge = '<span class="status-badge status-yes">✓ Есть</span>';
        else if (status === 'partial') statusBadge = '<span class="status-badge status-partial">~ Частично</span>';
        statusBadgeContainer.innerHTML = statusBadge;

        noteContainer.textContent = (ev && ev.evidence_note) ? ev.evidence_note : 'Пояснение реализации отсутствует или возможность не поддерживается.';

        if (ev && ev.evidence_link) {
          let link = ev.evidence_link;
          let fullUrl = link;
          if (tool && tool.repository_url && !link.startsWith('http')) {
            // Build GitHub/GitLab link if relative
            const repo = tool.repository_url.replace(/\/+$/, '');
            let branch = 'master';
            if (tool.tool_id === 'pysatl-mpest') {
              branch = 'refactor/rework-arch';
            } else if (repo.includes('scikit-learn')) {
              branch = 'main';
            }
            fullUrl = `${repo}/blob/${branch}/${link}`;
          }
          linkContainer.innerHTML = `
            <a href="${fullUrl}" target="_blank" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline break-all font-mono inline-flex items-center gap-1">
              <span>🔗</span> ${ev.evidence_link}
            </a>
          `;
        } else {
          linkContainer.innerHTML = '<span class="text-slate-400 dark:text-slate-500 italic">Ссылка на строку кода не указана</span>';
        }

        modalEvidence.classList.remove('hidden');
      }

      function closeEvidenceModal() {
        modalEvidence.classList.add('hidden');
      }

      // -----------------------------------------------------------
      // Literature Drawer
      // -----------------------------------------------------------
      function openLiteratureDrawer(reqId) {
        activeReqForDrawer = reqMap.get(reqId);
        if (!activeReqForDrawer) return;

        document.getElementById('lit-req-id').textContent = activeReqForDrawer.req_id;
        document.getElementById('lit-req-name').textContent = activeReqForDrawer.name;
        document.getElementById('lit-req-desc').textContent = activeReqForDrawer.description;
        document.getElementById('lit-req-type').textContent = category_names[activeReqForDrawer.type] || activeReqForDrawer.type;

        const prioSpan = document.getElementById('lit-req-priority');
        prioSpan.textContent = activeReqForDrawer.priority;
        prioSpan.className = `px-2 py-0.5 rounded text-xs font-semibold uppercase priority-${activeReqForDrawer.priority}`;

        // Reset search inside drawer
        document.getElementById('lit-filter-text').value = '';

        renderDrawerArticles();

        drawerLit.classList.remove('hidden');
        requestAnimationFrame(() => {
          drawerLit.querySelector('.drawer').classList.remove('translate-x-full');
        });
      }

      function closeLiteratureDrawer() {
        drawerLit.querySelector('.drawer').classList.add('translate-x-full');
        setTimeout(() => {
          drawerLit.classList.add('hidden');
        }, 200);
      }

      function renderDrawerArticles() {
        if (!activeReqForDrawer) return;

        const allArticles = reqArticlesMap.get(activeReqForDrawer.req_id) || [];
        document.getElementById('lit-total-count').textContent = allArticles.length;

        const minCit = parseInt(document.getElementById('lit-filter-citations').value, 10);
        const role = document.getElementById('lit-filter-role').value;
        const sort = document.getElementById('lit-filter-sort').value;
        const limit = document.getElementById('lit-filter-limit').value;
        const q = document.getElementById('lit-filter-text').value.toLowerCase().trim();

        let filtered = allArticles.filter(item => {
          const c = item.article.citations_count || 0;
          if (c < minCit) return false;
          if (role !== 'all' && item.role !== role) return false;
          if (q) {
            const t = item.article.title.toLowerCase();
            const a = item.article.authors.toLowerCase();
            const n = item.context_note.toLowerCase();
            if (!t.includes(q) && !a.includes(q) && !n.includes(q)) return false;
          }
          return true;
        });

        // Sorting
        if (sort === 'citations-desc') {
          filtered.sort((a, b) => (b.article.citations_count || 0) - (a.article.citations_count || 0));
        } else if (sort === 'year-desc') {
          filtered.sort((a, b) => (parseInt(b.article.year, 10) || 0) - (parseInt(a.article.year, 10) || 0));
        } else if (sort === 'year-asc') {
          filtered.sort((a, b) => (parseInt(a.article.year, 10) || 0) - (parseInt(b.article.year, 10) || 0));
        }

        document.getElementById('lit-matched-count').textContent = filtered.length;

        // Limit
        const displayList = (limit === 'all') ? filtered : filtered.slice(0, parseInt(limit, 10));

        const listContainer = document.getElementById('lit-articles-list');
        if (displayList.length === 0) {
          listContainer.innerHTML = `
            <div class="py-12 text-center text-slate-400 dark:text-slate-500">
              Статей по заданным критериям фильтрации не найдено.
            </div>
          `;
          return;
        }

        let html = '';
        displayList.forEach(item => {
          const art = item.article;
          const doi = art.doi || art.url;
          const hasDoiLink = doi && doi.startsWith('http');
          const cit = art.citations_count || 0;
          const citStr = cit.toLocaleString('ru-RU');

          let roleBadgeClass = 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700';
          let roleTitle = item.role;
          if (item.role === 'foundation') {
            roleBadgeClass = 'bg-purple-100 dark:bg-purple-950/70 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800 font-semibold';
            roleTitle = 'Теоретический базис (foundation)';
          } else if (item.role === 'method') {
            roleBadgeClass = 'bg-blue-100 dark:bg-blue-950/70 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800 font-semibold';
            roleTitle = 'Алгоритмический метод (method)';
          } else if (item.role === 'benchmark') {
            roleBadgeClass = 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-semibold';
            roleTitle = 'Бенчмарк (benchmark)';
          }

          html += `
            <div class="pt-3 first:pt-0">
              <div class="flex items-start justify-between gap-3 mb-1">
                <h4 class="font-bold text-slate-900 dark:text-slate-100 text-sm leading-snug">
                  ${hasDoiLink ? `<a href="${doi}" target="_blank" class="hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline">${art.title}</a>` : art.title}
                </h4>
                <div class="flex items-center gap-1.5 shrink-0">
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${cit >= 500 ? 'bg-amber-100 dark:bg-amber-950/80 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-700' : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700'}">
                    🔥 ${citStr}
                  </span>
                </div>
              </div>

              <div class="text-xs text-slate-600 dark:text-slate-400 mb-2">
                <span class="font-medium text-slate-800 dark:text-slate-200">${art.authors}</span> · <span class="font-semibold text-slate-900 dark:text-slate-100">${art.year}</span>
              </div>

              <div class="flex items-center gap-2 mb-2 flex-wrap">
                <span class="px-2 py-0.5 rounded text-[11px] ${roleBadgeClass}">${roleTitle}</span>
                <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500">[ID: ${art.article_id}]</span>
                ${hasDoiLink ? `<a href="${doi}" target="_blank" class="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline inline-flex items-center gap-0.5"><span>DOI:</span> ${doi.replace('https://doi.org/', '')} ↗</a>` : ''}
              </div>

              ${item.context_note ? `
                <div class="p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs italic leading-relaxed">
                  <b class="not-italic text-slate-900 dark:text-slate-100">Обоснование для требования:</b> ${item.context_note}
                </div>
              ` : ''}
            </div>
          `;
        });

        listContainer.innerHTML = html;
      }

      // -----------------------------------------------------------
      // Custom Tool Selector Modal Logic
      // -----------------------------------------------------------
      function openToolsModal() {
        // Sync checkboxes with current selection
        document.querySelectorAll('.tool-checkbox').forEach(cb => {
          cb.checked = selectedToolIds.includes(cb.value);
        });
        modalTools.classList.remove('hidden');
      }

      function closeToolsModal() {
        modalTools.classList.add('hidden');
      }

      function applySelectedTools() {
        const checked = Array.from(document.querySelectorAll('.tool-checkbox:checked')).map(cb => cb.value);
        if (checked.length === 0) {
          alert('Необходимо выбрать хотя бы один инструмент.');
          return;
        }
        // Always place pysatl-mpest first if present
        if (checked.includes('pysatl-mpest')) {
          selectedToolIds = ['pysatl-mpest', ...checked.filter(id => id !== 'pysatl-mpest')];
        } else {
          selectedToolIds = checked;
        }
        closeToolsModal();
        renderMatrix();
        showToast(`Выбрано инструментов: ${selectedToolIds.length}`);
      }

      // -----------------------------------------------------------
      // Export Helpers
      // -----------------------------------------------------------
      function exportFilteredToMarkdown() {
        const filteredReqs = getFilteredRequirements();
        let md = `# Сравнительная матрица требований\\n\\n`;
        md += `| Код | Требование | Приоритет | ` + selectedToolIds.map(tid => `\`${tid}\``).join(' | ') + ` | Статьи (N) |\\n`;
        md += `|:---|:---|:---:|` + selectedToolIds.map(() => `:---:`).join('|') + `|:---:|\\n`;

        filteredReqs.forEach(r => {
          const nArts = (reqArticlesMap.get(r.req_id) || []).length;
          const toolStatuses = selectedToolIds.map(tid => {
            const ev = evalMap.get(`${tid}::${r.req_id}`);
            const s = ev ? ev.status : 'no';
            if (s === 'yes') return '🟢 Есть';
            if (s === 'partial') return '🟡 Частично';
            return '🔴 Нет';
          });
          md += `| **${r.req_id}** | ${r.name} | \`${r.priority}\` | ` + toolStatuses.join(' | ') + ` | ${nArts} |\\n`;
        });

        navigator.clipboard.writeText(md).then(() => {
          showToast('Markdown скопирован в буфер обмена!');
        }).catch(() => {
          showToast('Ошибка копирования');
        });
      }

      function exportFilteredToCSV() {
        const filteredReqs = getFilteredRequirements();
        let csvContent = 'req_id,name,priority,type,' + selectedToolIds.join(',') + ',articles_count\\n';

        filteredReqs.forEach(r => {
          const nArts = (reqArticlesMap.get(r.req_id) || []).length;
          const statuses = selectedToolIds.map(tid => {
            const ev = evalMap.get(`${tid}::${r.req_id}`);
            return ev ? ev.status : 'no';
          });
          const row = [
            `"${r.req_id}"`,
            `"${r.name.replace(/"/g, '""')}"`,
            `"${r.priority}"`,
            `"${r.type}"`,
            ...statuses.map(s => `"${s}"`),
            nArts
          ];
          csvContent += row.join(',') + '\\n';
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mpest_matrix_${currentCategory}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('CSV-файл скачан!');
      }

      function copyActiveReqLiteratureMarkdown() {
        if (!activeReqForDrawer) return;
        const allArticles = reqArticlesMap.get(activeReqForDrawer.req_id) || [];
        let md = `### Литература для требования [${activeReqForDrawer.req_id}] ${activeReqForDrawer.name}\\n\\n`;
        allArticles.forEach((item, idx) => {
          const art = item.article;
          md += `${idx + 1}. **${art.authors}** (${art.year}). *«${art.title}»*. Цитирований: **${art.citations_count}**. DOI: ${art.doi || art.url}\\n`;
          if (item.context_note) md += `   > *Обоснование:* ${item.context_note}\\n`;
        });
        navigator.clipboard.writeText(md).then(() => {
          showToast('Список литературы (Markdown) скопирован!');
        });
      }

      function copyActiveReqBibTeX() {
        if (!activeReqForDrawer) return;
        const allArticles = reqArticlesMap.get(activeReqForDrawer.req_id) || [];
        let bib = '';
        allArticles.forEach(item => {
          const art = item.article;
          const firstAuthor = art.authors ? art.authors.split(';')[0].trim().split(' ').pop().toLowerCase() : 'unknown';
          const citeKey = `${firstAuthor}${art.year}_${art.article_id.toLowerCase()}`;
          bib += `@article{${citeKey},\\n`;
          bib += `  author = {${art.authors}},\\n`;
          bib += `  title = {${art.title}},\\n`;
          bib += `  year = {${art.year}},\\n`;
          if (art.doi) bib += `  doi = {${art.doi}},\\n`;
          if (art.url) bib += `  url = {${art.url}},\\n`;
          bib += `  note = {Citations: ${art.citations_count}}\\n`;
          bib += `}\\n\\n`;
        });
        navigator.clipboard.writeText(bib).then(() => {
          showToast('BibTeX скопирован в буфер обмена!');
        });
      }

      // -----------------------------------------------------------
      // Event Listeners
      // -----------------------------------------------------------
      inputSearch.addEventListener('input', (e) => {
        searchQuery = e.target.value.trim();
        renderMatrix();
      });

      selectCategory.addEventListener('change', (e) => {
        currentCategory = e.target.value;
        renderMatrix();
      });

      selectPreset.addEventListener('change', (e) => {
        currentPreset = e.target.value;
        renderMatrix();
      });

      // Ecosystem tabs
      ecoTabs.addEventListener('click', (e) => {
        const btn = e.target.closest('.eco-btn');
        if (!btn) return;
        ecoTabs.querySelectorAll('.eco-btn').forEach(b => {
          b.className = 'eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white';
        });
        btn.className = 'eco-btn px-2.5 py-1 rounded font-medium text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/70';

        const eco = btn.getAttribute('data-eco');
        currentEco = eco;
        if (eco === 'all') {
          selectedToolIds = tools.map(t => t.tool_id);
        } else {
          selectedToolIds = ECOSYSTEM_TOOL_IDS[eco] || tools.map(t => t.tool_id);
        }

        // Keep mpest first
        if (tools.some(t => t.tool_id === 'pysatl-mpest') && !selectedToolIds.includes('pysatl-mpest')) {
          selectedToolIds = ['pysatl-mpest', ...selectedToolIds];
        }

        renderMatrix();
      });

      // Reset filters
      document.getElementById('btn-reset-filters').addEventListener('click', () => {
        inputSearch.value = '';
        searchQuery = '';
        selectCategory.value = 'all';
        currentCategory = 'all';
        selectPreset.value = 'all';
        currentPreset = 'all';
        selectedToolIds = tools.map(t => t.tool_id);
        ecoTabs.querySelector('[data-eco="all"]').click();
        renderMatrix();
        showToast('Все фильтры сброшены');
      });

      // Drawer listeners
      document.getElementById('btn-close-drawer').addEventListener('click', closeLiteratureDrawer);
      document.getElementById('drawer-backdrop').addEventListener('click', closeLiteratureDrawer);
      document.getElementById('lit-filter-citations').addEventListener('change', renderDrawerArticles);
      document.getElementById('lit-filter-role').addEventListener('change', renderDrawerArticles);
      document.getElementById('lit-filter-sort').addEventListener('change', renderDrawerArticles);
      document.getElementById('lit-filter-limit').addEventListener('change', renderDrawerArticles);
      document.getElementById('lit-filter-text').addEventListener('input', renderDrawerArticles);
      document.getElementById('btn-copy-lit-markdown').addEventListener('click', copyActiveReqLiteratureMarkdown);
      document.getElementById('btn-copy-lit-bibtex').addEventListener('click', copyActiveReqBibTeX);

      // Modal listeners
      document.getElementById('btn-close-evidence').addEventListener('click', closeEvidenceModal);
      document.getElementById('btn-close-evidence-ok').addEventListener('click', closeEvidenceModal);
      document.getElementById('modal-evidence-backdrop').addEventListener('click', closeEvidenceModal);

      document.getElementById('btn-custom-tools').addEventListener('click', openToolsModal);
      document.getElementById('btn-close-tools').addEventListener('click', closeToolsModal);
      document.getElementById('modal-tools-backdrop').addEventListener('click', closeToolsModal);
      document.getElementById('btn-apply-tools').addEventListener('click', applySelectedTools);

      document.getElementById('btn-select-all-tools').addEventListener('click', () => {
        document.querySelectorAll('.tool-checkbox').forEach(cb => cb.checked = true);
      });
      document.getElementById('btn-select-only-mpest').addEventListener('click', () => {
        document.querySelectorAll('.tool-checkbox').forEach(cb => cb.checked = (cb.value === 'pysatl-mpest'));
      });
      document.getElementById('btn-select-python-tools').addEventListener('click', () => {
        document.querySelectorAll('.tool-checkbox').forEach(cb => {
          cb.checked = ECOSYSTEM_TOOL_IDS.python.includes(cb.value);
        });
      });
      document.getElementById('btn-select-r-tools').addEventListener('click', () => {
        document.querySelectorAll('.tool-checkbox').forEach(cb => {
          cb.checked = ECOSYSTEM_TOOL_IDS.r.includes(cb.value);
        });
      });

      document.getElementById('btn-help').addEventListener('click', () => modalHelp.classList.remove('hidden'));
      document.getElementById('btn-close-help').addEventListener('click', () => modalHelp.classList.add('hidden'));
      document.getElementById('btn-close-help-ok').addEventListener('click', () => modalHelp.classList.add('hidden'));
      document.getElementById('modal-help-backdrop').addEventListener('click', () => modalHelp.classList.add('hidden'));

      // Export buttons
      document.getElementById('btn-export-markdown').addEventListener('click', exportFilteredToMarkdown);
      document.getElementById('btn-export-csv').addEventListener('click', exportFilteredToCSV);

      // Keyboard Esc to close modals
      window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeLiteratureDrawer();
          closeEvidenceModal();
          closeToolsModal();
          modalHelp.classList.add('hidden');
        }
      });

      // Theme toggle logic
      const btnThemeToggle = document.getElementById('btn-theme-toggle');
      const themeToggleIcon = document.getElementById('theme-toggle-icon');
      const themeToggleText = document.getElementById('theme-toggle-text');

      function syncThemeButton() {
        const isDark = document.documentElement.classList.contains('dark');
        if (themeToggleIcon) themeToggleIcon.textContent = isDark ? '☀️' : '🌙';
        if (themeToggleText) themeToggleText.textContent = isDark ? 'Светлая' : 'Темная';
      }

      syncThemeButton();

      if (btnThemeToggle) {
        btnThemeToggle.addEventListener('click', () => {
          const isDark = document.documentElement.classList.contains('dark');
          if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.theme = 'light';
            showToast('Включена светлая тема');
          } else {
            document.documentElement.classList.add('dark');
            localStorage.theme = 'dark';
            showToast('Включена темная тема');
          }
          syncThemeButton();
        });
      }

      // Initial render
      renderMatrix();
    })();
  </script>
</body>
</html>
"""


def generate_dashboard(data_dir: Path, output_file: Path):
    from datetime import datetime
    dataset = load_dataset(data_dir)
    raw_json = json.dumps(dataset, ensure_ascii=False)

    tools = dataset["tools"]
    reqs = dataset["requirements"]
    arts = dataset["articles"]

    num_tools = len(tools)
    num_reqs = len(reqs)
    num_arts = len(arts)
    num_python = len([t for t in tools if t.get("ecosystem") == "Python"])
    num_r = len([t for t in tools if "R" in t.get("ecosystem", "")])
    num_julia_cpp = len([t for t in tools if not "R" in t.get("ecosystem", "") and ("Julia" in t.get("ecosystem", "") or "C++" in t.get("ecosystem", ""))])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = HTML_TEMPLATE.replace("__RAW_JSON_DATA__", raw_json)
    html_content = html_content.replace("__BUILD_TIMESTAMP__", f"Собрано: {now_str}")
    html_content = html_content.replace("__NUM_TOOLS__", str(num_tools))
    html_content = html_content.replace("__NUM_REQS__", str(num_reqs))
    html_content = html_content.replace("__NUM_ARTICLES__", str(num_arts))
    html_content = html_content.replace("__NUM_PYTHON__", str(num_python))
    html_content = html_content.replace("__NUM_R__", str(num_r))
    html_content = html_content.replace("__NUM_JULIA_CPP__", str(num_julia_cpp))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Дашборд успешно сгенерирован: {output_file} ({output_file.stat().st_size / 1024:.1f} KB)")




USECASES_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Прикладные сценарии и открытые бенчмарки — pysatl-mpest</title>
  <!-- Early Dark Mode Detection -->
  <script>
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  </script>
  <!-- Tailwind CSS via CDN with fallback styling -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
            }
          }
        }
      }
    }
  </script>
  <style>
    .hidden { display: none !important; }
    body { overflow-x: hidden; }
    .table-container {
      max-height: calc(100vh - 280px);
      overflow: auto;
      scrollbar-width: thin;
    }
    .dark .table-container { scrollbar-color: #475569 #0f172a; }
    .dark .table-container::-webkit-scrollbar { background-color: #0f172a; }
    .dark .table-container::-webkit-scrollbar-thumb { background-color: #334155; border-radius: 4px; }
    .dark .table-container::-webkit-scrollbar-thumb:hover { background-color: #475569; }

    /* Custom sticky headers */
    .sticky-th { position: sticky; top: 0; z-index: 20; }
    .sticky-col-1 { position: sticky; left: 0; z-index: 10; }
    .sticky-header-corner { position: sticky; left: 0; top: 0; z-index: 30; }

    /* Guaranteed Drawer Animation with !important */
    #drawer {
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    #drawer.is-open {
      transform: translateX(0) !important;
      pointer-events: auto !important;
      visibility: visible !important;
    }
    #drawer.is-closed {
      transform: translateX(100%) !important;
      pointer-events: none !important;
      visibility: hidden !important;
    }
  </style>
</head>
<body class="bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-indigo-500 selection:text-white transition-colors duration-200">

  <!-- Header Section -->
  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40 shadow-sm transition-colors duration-200">
    <div class="max-w-[1920px] mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
      <!-- Title & Branding -->
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center text-white font-black text-xl shadow-md">
          🎯
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-bold tracking-tight text-slate-900 dark:text-white">Прикладные сценарии и открытые бенчмарки</h1>
            <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
              pysatl-mpest
            </span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            5-осевая таксономия задач, 52 открытых исследования и матрица готовности 27 инструментов оценивания
          </p>
        </div>
      </div>

      <!-- Quick Metrics & Navigation -->
      <div class="flex items-center flex-wrap gap-2 text-xs">
        <a href="dashboard.html" class="px-3 py-1.5 bg-indigo-50 dark:bg-indigo-950/70 hover:bg-indigo-100 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-semibold rounded-lg border border-indigo-200 dark:border-indigo-800 shadow-sm transition flex items-center gap-1.5" title="Перейти к матрице требований">
          <span>←</span> Матрица требований (86 фич)
        </a>

        <div class="hidden xl:flex items-center gap-2 bg-slate-50 dark:bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300">
          <span class="font-bold text-slate-900 dark:text-slate-100">10 сценариев</span>
          <span class="text-slate-300 dark:text-slate-600">|</span>
          <span class="font-bold text-slate-900 dark:text-slate-100">52 бенчмарка</span>
          <span class="text-slate-300 dark:text-slate-600">|</span>
          <span class="font-bold text-slate-900 dark:text-slate-100">27 библиотек</span>
          <span class="text-slate-300 dark:text-slate-600">|</span>
          <span class="font-bold text-emerald-600 dark:text-emerald-400">100% открытые данные</span>
        </div>

        <button id="btn-theme-toggle" class="px-2.5 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-medium rounded-lg border border-slate-300 dark:border-slate-700 shadow-sm transition flex items-center gap-1.5" title="Переключить тему оформления">
          <span id="theme-toggle-icon">🌙</span> <span id="theme-toggle-text">Темная</span>
        </button>
      </div>
    </div>

    <!-- View Switcher & Filter Toolbar -->
    <div class="bg-slate-50 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 px-4 py-2.5">
      <div class="max-w-[1920px] mx-auto flex flex-wrap items-center justify-between gap-3">
        
        <!-- Left: View Tabs -->
        <div class="flex items-center gap-1.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-0.5 shadow-sm text-xs">
          <button id="tab-cards" class="view-tab-btn px-3 py-1.5 rounded-md font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/70 transition flex items-center gap-1.5">
            <span>📑</span> Карточки сценариев (10)
          </button>
          <button id="tab-matrix" class="view-tab-btn px-3 py-1.5 rounded-md font-semibold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-1.5">
            <span>📊</span> Матрица готовности библиотек (27×10)
          </button>
          <button id="tab-audit" class="view-tab-btn px-3 py-1.5 rounded-md font-semibold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-1.5">
            <span>🔬</span> Аудит воспроизводимости (52 статьи)
          </button>
        </div>

        <!-- Center: Search Input -->
        <div class="relative w-64 flex-grow max-w-xs">
          <input type="text" id="input-search" placeholder="Поиск по сценарию, датасету, автору, библиотеке..."
                 class="w-full pl-8 pr-3 py-1.5 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm">
          <span class="absolute left-2.5 top-2 text-slate-400 dark:text-slate-500 text-xs">🔍</span>
        </div>

        <!-- Right: 5-Axis Filters Dropdowns -->
        <div class="flex flex-wrap items-center gap-2">
          <!-- Domain Filter -->
          <select id="filter-domain" class="py-1.5 px-2 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
            <option value="all">Все области (10)</option>
            <option value="Астрофизика">Астрофизика</option>
            <option value="Экология и гидрохимия">Экология</option>
            <option value="Фармакогенетика и биомедицина">Фармакогенетика</option>
            <option value="Метрология и историческое материаловедение">Метрология</option>
            <option value="Гидрогеология и геофизика">Геология</option>
            <option value="Промышленная надежность">Надежность</option>
            <option value="Метеорология и ветроэнергетика">Метеорология</option>
            <option value="Актуарные расчеты и финансовые риски">Финансы и риски</option>
            <option value="Иммунология и проточная цитометрия">Цитометрия</option>
            <option value="Сетевой трафик и телекоммуникации">Сетевой трафик</option>
          </select>

          <!-- Mixture Type Filter -->
          <select id="filter-mixture-type" class="py-1.5 px-2 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
            <option value="all">Смесь: Все</option>
            <option value="homogeneous">Однородная (homogeneous)</option>
            <option value="heterogeneous">Разнородная (heterogeneous)</option>
          </select>

          <!-- Morphology Filter -->
          <select id="filter-morphology" class="py-1.5 px-2 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
            <option value="all">Морфология: Все</option>
            <option value="symmetric">Симметричные</option>
            <option value="skewed">Скошенные</option>
            <option value="semi_bounded">Полуограниченные [0, ∞)</option>
            <option value="heavy_tailed">Тяжелохвостые</option>
          </select>

          <!-- Prior Knowledge (Status of K) Filter -->
          <select id="filter-prior-knowledge" class="py-1.5 px-2 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
            <option value="all">Число K: Все (10)</option>
            <option value="known">K известно (4 сценария)</option>
            <option value="unknown">K неизвестно (6 сценариев)</option>
          </select>

          <!-- Observation Regime Filter -->
          <select id="filter-observation-regime" class="py-1.5 px-2 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
            <option value="all">Режим: Все</option>
            <option value="direct">Прямые отсчеты</option>
            <option value="censored">Цензурированные</option>
            <option value="binned">Сгруппированные (binned)</option>
            <option value="imbalanced">Дисбаланс / редкие</option>
          </select>

          <!-- Sample Regime Filter -->
          <select id="filter-sample-regime" class="py-1.5 px-2 text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium">
            <option value="all">Выборка: Все</option>
            <option value="small">Малая (N &lt; 100)</option>
            <option value="moderate">Умеренная (100–10k)</option>
            <option value="large">Большая (10k–100k)</option>
            <option value="massive">Big Data (N &ge; 1M)</option>
          </select>

          <!-- Reset Button -->
          <button id="btn-reset-filters" class="px-2.5 py-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 font-medium transition">
            Сброс
          </button>
        </div>

      </div>
    </div>
  </header>

  <!-- Main View Area -->
  <main class="flex-grow max-w-[1920px] w-full mx-auto p-4">

    <!-- Active Filter Counter -->
    <div id="filter-status-bar" class="mb-3 text-xs text-slate-500 dark:text-slate-400 flex items-center justify-between">
      <span id="filter-status-text">Показано: 10 из 10 сценариев</span>
    </div>

    <!-- VIEW 1: Cards View -->
    <div id="view-cards-container" class="space-y-4">
      <div id="cards-grid" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <!-- Rendered via JS -->
      </div>
      <div id="cards-empty" class="hidden text-center py-16 text-slate-400 dark:text-slate-500 text-sm">
        <div class="text-3xl mb-2">🔍</div>
        Ни один прикладной сценарий не соответствует выбранным критериям фильтрации.
      </div>
    </div>

    <!-- VIEW 2: Readiness Matrix View -->
    <div id="view-matrix-container" class="hidden bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
      <!-- Toolbar inside Matrix -->
      <div class="p-3 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-50 dark:bg-slate-900/50 text-xs">
        <div class="flex items-center flex-wrap gap-2">
          <span class="font-semibold text-slate-700 dark:text-slate-300">Готовность к сценариям:</span>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> ≥80% Высокая
          </span>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> 50–79% Частичная
          </span>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> &lt;50% Недостаточная
          </span>
          <span class="text-slate-400 dark:text-slate-500">|</span>
          <span class="inline-flex items-center gap-1 text-slate-600 dark:text-slate-400">
            <span>✓</span> Все крит. требования закрыты
          </span>
          <span class="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400">
            <span>⚠</span> Не хватает критических фич
          </span>
        </div>

        <!-- Ecosystem filter for matrix -->
        <div class="flex items-center gap-1 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-0.5">
          <button data-matrix-eco="all" class="matrix-eco-btn px-2.5 py-1 rounded font-medium text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/70">Все (27)</button>
          <button data-matrix-eco="Python" class="matrix-eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white">Python (8)</button>
          <button data-matrix-eco="R" class="matrix-eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white">R (14)</button>
          <button data-matrix-eco="other" class="matrix-eco-btn px-2.5 py-1 rounded font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white">Julia/C++ (5)</button>
        </div>
      </div>

      <!-- Matrix Table -->
      <div class="table-container">
        <table class="w-full text-left border-collapse text-xs min-w-[1100px]" id="table-matrix">
          <!-- Rendered via JS -->
        </table>
      </div>
    </div>

    <!-- VIEW 3: Reproducibility & Open Science Audit View -->
    <div id="view-audit-container" class="hidden space-y-4">
      <!-- Top Audit KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Всего эмпирических публикаций</div>
          <div class="text-2xl font-bold text-slate-900 dark:text-white mt-1">52 исследования</div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">49 уникальных статей в 10 доменах</div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">Полная воспроизводимость (full)</div>
          <div class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1" id="audit-stat-full">24 статьи</div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Открытый датасет + открытый код / R-пакет</div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div class="text-xs text-sky-600 dark:text-sky-400 font-medium">Открытые данные (data_only)</div>
          <div class="text-2xl font-bold text-sky-700 dark:text-sky-300 mt-1" id="audit-stat-data">28 статей</div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Датасет в открытом доступе / в тексте статьи</div>
        </div>

        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div class="text-xs text-indigo-600 dark:text-indigo-400 font-medium">Доля открытости данных</div>
          <div class="text-2xl font-bold text-indigo-700 dark:text-indigo-300 mt-1">100%</div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Все 52 бенчмарка доступны публично</div>
        </div>
      </div>

      <!-- Audit Articles Table -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div class="p-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center justify-between">
          <h3 class="font-bold text-xs text-slate-900 dark:text-white">Реестр открытых прикладных бенчмарков и их воспроизводимость</h3>
          <span class="text-xs text-slate-500 dark:text-slate-400">Прямые ссылки на открытые репозитории (Zenodo, CRAN, GitHub, Kaggle, DOI)</span>
        </div>
        <div class="table-container">
          <table class="w-full text-left border-collapse text-xs" id="table-audit">
            <!-- Rendered via JS -->
          </table>
        </div>
      </div>
    </div>

  </main>

  <!-- Slide-over Drawer for Use Case Details -->
  <div id="drawer-backdrop" class="hidden fixed inset-0 bg-slate-950/50 backdrop-blur-sm z-40 transition-opacity duration-300 opacity-0" onclick="closeDrawer()"></div>
  <aside id="drawer" class="is-closed fixed top-0 right-0 h-full w-full max-w-2xl bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl z-50 flex flex-col" style="transform: translateX(100%);">
    
    <!-- Drawer Header -->
    <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex items-start justify-between gap-4 bg-slate-50 dark:bg-slate-900/80">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span id="drawer-uc-id" class="px-2 py-0.5 text-xs font-black rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
            UC-01
          </span>
          <span id="drawer-uc-domain" class="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Астрофизика
          </span>
        </div>
        <h2 id="drawer-uc-name" class="text-base font-bold text-slate-900 dark:text-white leading-snug">
          Название сценария
        </h2>
      </div>
      <button id="btn-close-drawer" type="button" onclick="closeDrawer()" class="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 transition" title="Закрыть панель (Escape)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Drawer Content Scrollable -->
    <div class="flex-grow overflow-y-auto p-4 space-y-5 text-xs">
      <!-- Verbal Description -->
      <div>
        <h4 class="font-bold text-slate-900 dark:text-slate-100 mb-1.5 flex items-center gap-1.5">
          <span>📖</span> Описание прикладной задачи
        </h4>
        <p id="drawer-uc-desc" class="text-slate-600 dark:text-slate-300 leading-relaxed text-justify bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-200 dark:border-slate-800">
          Описание...
        </p>
      </div>

      <!-- 5-Axis Taxonomy Pills -->
      <div>
        <h4 class="font-bold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-1.5">
          <span>📐</span> Классификация по 5 осям таксономии
        </h4>
        <div class="grid grid-cols-2 gap-2" id="drawer-taxonomy-grid">
          <!-- Rendered via JS -->
        </div>
      </div>

      <!-- Requirements & Academic Rationales (Grouped by Category) -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <h4 class="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <span>⚙️</span> Требования к библиотеке
            </h4>
            <span id="drawer-reqs-count" class="text-[11px] font-semibold text-slate-500 dark:text-slate-400"></span>
          </div>

          <!-- Grouping Toggle: by Category or by Importance -->
          <div class="flex items-center bg-slate-200 dark:bg-slate-800 p-0.5 rounded text-[10px]">
            <button type="button" id="btn-group-by-cat" class="px-2 py-0.5 rounded font-semibold text-indigo-700 dark:text-indigo-300 bg-white dark:bg-slate-900 shadow-sm transition">
              По группам
            </button>
            <button type="button" id="btn-group-by-imp" class="px-2 py-0.5 rounded font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition">
              По важности
            </button>
          </div>
        </div>
        <div id="drawer-reqs-list" class="space-y-3">
          <!-- Rendered via JS -->
        </div>
      </div>

      <!-- Benchmark Datasets & Associated Papers -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <h4 class="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
            <span>📚</span> Открытые датасеты и публикации
          </h4>
          <span id="drawer-articles-count" class="text-[11px] font-semibold text-slate-500 dark:text-slate-400"></span>
        </div>
        <div id="drawer-articles-list" class="space-y-2">
          <!-- Rendered via JS -->
        </div>
      </div>

      <!-- Ecosystem Readiness Ranking for this UC -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <h4 class="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
            <span>🏆</span> Рейтинг готовности библиотек
          </h4>
          <button id="btn-toggle-all-rankings" type="button" class="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">
            Показать все 27
          </button>
        </div>
        <div id="drawer-readiness-ranking" class="space-y-1.5 bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-200 dark:border-slate-800">
          <!-- Rendered via JS -->
        </div>
      </div>
    </div>

    <!-- Drawer Footer -->
    <div class="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80 flex items-center justify-between">
      <span class="text-[11px] text-slate-500 dark:text-slate-400">Нажмите Escape или кликните вне окна для закрытия</span>
      <button type="button" onclick="closeDrawer()" class="px-4 py-1.5 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold rounded-lg text-xs transition">
        Закрыть
      </button>
    </div>
  </aside>

  <!-- Embedded Data & Client Application -->
  <script>
    const RAW_DATA = __RAW_USECASES_DATA__;

    // State
    const state = {
      activeView: 'cards', // 'cards' | 'matrix' | 'audit'
      searchQuery: '',
      filterDomain: 'all',
      filterMixtureType: 'all',
      filterMorphology: 'all',
      filterPriorKnowledge: 'all',
      filterObservationRegime: 'all',
      filterSampleRegime: 'all',
      filterMatrixEco: 'all',
      selectedUseCaseId: null,
      showAllRankings: false,
      drawerReqsGrouping: 'category' // 'category' | 'importance'
    };

    // Category Metadata matching dashboard.html
    const CATEGORY_META = {
      estimation: { title: 'Оценивание параметров (EST)', icon: '📈', prefix: 'EST' },
      structure: { title: 'Структура смеси и выбор K (STRUC)', icon: '🧩', prefix: 'STRUC' },
      initialization: { title: 'Инициализация параметров (INIT)', icon: '🎯', prefix: 'INIT' },
      technical: { title: 'Архитектура и API (TECH)', icon: '⚙️', prefix: 'TECH' },
      representation: { title: 'Представление смеси и интерфейс (REPR)', icon: '📦', prefix: 'REPR' },
      performance: { title: 'Производительность и параллелизация (PERF)', icon: '⚡', prefix: 'PERF' },
      visualization: { title: 'Визуализация и графики (VIS)', icon: '📊', prefix: 'VIS' },
      diagnostics: { title: 'Статистическая диагностика и бенчмарки (DIAG)', icon: '🔬', prefix: 'DIAG' },
      proprietary: { title: 'Проприетарные возможности (PROP)', icon: '💎', prefix: 'PROP' },
      infrastructure: { title: 'Инженерия качества и CI (INFRA)', icon: '🛠️', prefix: 'INFRA' }
    };

    const CATEGORY_ORDER = [
      'estimation',
      'structure',
      'initialization',
      'technical',
      'representation',
      'performance',
      'visualization',
      'diagnostics',
      'proprietary',
      'infrastructure'
    ];

    // DOM Elements
    const el = {
      tabCards: document.getElementById('tab-cards'),
      tabMatrix: document.getElementById('tab-matrix'),
      tabAudit: document.getElementById('tab-audit'),
      viewCards: document.getElementById('view-cards-container'),
      viewMatrix: document.getElementById('view-matrix-container'),
      viewAudit: document.getElementById('view-audit-container'),
      cardsGrid: document.getElementById('cards-grid'),
      cardsEmpty: document.getElementById('cards-empty'),
      filterStatusBar: document.getElementById('filter-status-bar'),
      filterStatusText: document.getElementById('filter-status-text'),
      tableMatrix: document.getElementById('table-matrix'),
      tableAudit: document.getElementById('table-audit'),
      inputSearch: document.getElementById('input-search'),
      filterDomain: document.getElementById('filter-domain'),
      filterMixtureType: document.getElementById('filter-mixture-type'),
      filterMorphology: document.getElementById('filter-morphology'),
      filterPriorKnowledge: document.getElementById('filter-prior-knowledge'),
      filterObservationRegime: document.getElementById('filter-observation-regime'),
      filterSampleRegime: document.getElementById('filter-sample-regime'),
      btnResetFilters: document.getElementById('btn-reset-filters'),
      btnThemeToggle: document.getElementById('btn-theme-toggle'),
      themeToggleIcon: document.getElementById('theme-toggle-icon'),
      themeToggleText: document.getElementById('theme-toggle-text'),
      drawer: document.getElementById('drawer'),
      drawerBackdrop: document.getElementById('drawer-backdrop'),
      btnCloseDrawer: document.getElementById('btn-close-drawer'),
      drawerUcId: document.getElementById('drawer-uc-id'),
      drawerUcDomain: document.getElementById('drawer-uc-domain'),
      drawerUcName: document.getElementById('drawer-uc-name'),
      drawerUcDesc: document.getElementById('drawer-uc-desc'),
      drawerTaxonomyGrid: document.getElementById('drawer-taxonomy-grid'),
      drawerReqsCount: document.getElementById('drawer-reqs-count'),
      drawerReqsList: document.getElementById('drawer-reqs-list'),
      drawerArticlesCount: document.getElementById('drawer-articles-count'),
      drawerArticlesList: document.getElementById('drawer-articles-list'),
      drawerReadinessRanking: document.getElementById('drawer-readiness-ranking'),
      btnToggleAllRankings: document.getElementById('btn-toggle-all-rankings'),
      btnGroupByCat: document.getElementById('btn-group-by-cat'),
      btnGroupByImp: document.getElementById('btn-group-by-imp')
    };

    // Translation maps for 5-axis taxonomy
    const TAXONOMY_LABELS = {
      mixture_type: {
        'homogeneous': 'Однородная',
        'heterogeneous': 'Разнородная'
      },
      prior_knowledge: {
        'known_k_separated': 'K известно (K=2, разделенные моды)',
        'known_k_overlapping': 'K известно (K=2, перекрытие мод)',
        'known_k_competing': 'K известно (K=2, конкурирующие риски)',
        'known_k_heterogeneous': 'K известно (K=2, тело и хвост)',
        'unknown_k_separated': 'K неизвестно (моды разделены)',
        'unknown_k_overlapping': 'K неизвестно (перекрытие мод)',
        'unknown_k_heterogeneous': 'K неизвестно (разнородные законы)'
      },
      component_morphology: {
        'symmetric': 'Симметричные плотности',
        'skewed': 'Асимметричные (скошенные)',
        'semi_bounded': 'Полуограниченный [0, ∞)',
        'heavy_tailed': 'Тяжелохвостые (степенные)'
      },
      observation_regime: {
        'direct': 'Прямые непрерывные отсчеты',
        'censored': 'Цензурированные наблюдения',
        'binned': 'Сгруппированные (binned)',
        'imbalanced': 'Дисбаланс / редкие моды'
      },
      sample_regime: {
        'small': 'Малая (N < 100)',
        'moderate': 'Умеренная (100–10k)',
        'large': 'Большая (10k–100k)',
        'massive': 'Big Data (N ≥ 1M)'
      }
    };

    function formatNumber(numStr) {
      if (!numStr) return '—';
      const n = parseInt(numStr, 10);
      if (isNaN(n)) return numStr;
      return n.toLocaleString('ru-RU');
    }

    // Color mapper for readiness score
    function getReadinessClass(score, critOk) {
      if (!critOk) {
        return 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-900';
      }
      if (score >= 80) {
        return 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      }
      if (score >= 50) {
        return 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      }
      return 'bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700';
    }

    // Filter Logic for Use Cases
    function getFilteredUseCases() {
      const q = state.searchQuery.toLowerCase().trim();
      return RAW_DATA.usecases.filter(uc => {
        if (state.filterDomain !== 'all' && uc.domain !== state.filterDomain) return false;
        if (state.filterMixtureType !== 'all' && uc.mixture_type !== state.filterMixtureType) return false;
        if (state.filterMorphology !== 'all' && uc.component_morphology !== state.filterMorphology) return false;
        if (state.filterPriorKnowledge !== 'all') {
          if (state.filterPriorKnowledge === 'known' && !uc.prior_knowledge.startsWith('known')) return false;
          if (state.filterPriorKnowledge === 'unknown' && !uc.prior_knowledge.startsWith('unknown')) return false;
        }
        if (state.filterObservationRegime !== 'all' && uc.observation_regime !== state.filterObservationRegime) return false;
        if (state.filterSampleRegime !== 'all' && uc.sample_regime !== state.filterSampleRegime) return false;

        if (q) {
          const inName = uc.name.toLowerCase().includes(q);
          const inDesc = uc.description.toLowerCase().includes(q);
          const inDomain = uc.domain.toLowerCase().includes(q);
          const inId = uc.usecase_id.toLowerCase().includes(q);
          const arts = RAW_DATA.usecase_articles[uc.usecase_id] || [];
          const inArts = arts.some(a => 
            (a.dataset_name && a.dataset_name.toLowerCase().includes(q)) ||
            (a.title && a.title.toLowerCase().includes(q)) ||
            (a.authors && a.authors.toLowerCase().includes(q))
          );
          if (!inName && !inDesc && !inDomain && !inId && !inArts) return false;
        }

        return true;
      });
    }

    // Render Cards View
    function renderCards() {
      const filtered = getFilteredUseCases();
      el.cardsGrid.innerHTML = '';

      el.filterStatusText.innerText = `Показано: ${filtered.length} из ${RAW_DATA.usecases.length} сценариев`;

      if (filtered.length === 0) {
        el.cardsEmpty.classList.remove('hidden');
        return;
      }
      el.cardsEmpty.classList.add('hidden');

      filtered.forEach(uc => {
        const uid = uc.usecase_id;
        const arts = RAW_DATA.usecase_articles[uid] || [];
        const reqs = RAW_DATA.usecase_requirements[uid] || [];
        const primaryArt = arts.find(a => a.case_role === 'primary_benchmark') || arts[0] || {};
        
        const critReqs = reqs.filter(r => r.importance === 'critical');
        const desReqs = reqs.filter(r => r.importance === 'desirable');

        const card = document.createElement('div');
        card.className = 'bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:border-indigo-400 dark:hover:border-indigo-600 transition flex flex-col p-4 cursor-pointer';
        card.onclick = () => openDrawer(uid);

        card.innerHTML = `
          <!-- Card Header -->
          <div class="flex items-start justify-between gap-2 mb-2">
            <div>
              <div class="flex items-center gap-1.5 mb-1">
                <span class="px-2 py-0.5 text-[11px] font-black rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                  ${uc.usecase_id}
                </span>
                <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                  ${uc.domain}
                </span>
              </div>
              <h3 class="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                ${uc.name}
              </h3>
            </div>
          </div>

          <!-- Description Preview -->
          <p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 mb-3 text-justify leading-relaxed">
            ${uc.description}
          </p>

          <!-- 5-Axis Badges (including Status of K) -->
          <div class="flex flex-wrap gap-1.5 mb-2 text-[10px]">
            <!-- Axis 1: Mixture Type -->
            <span class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700">
              ${TAXONOMY_LABELS.mixture_type[uc.mixture_type] || uc.mixture_type}
            </span>

            <!-- Axis 3: Status of K (Known vs Unknown) -->
            ${uc.prior_knowledge && uc.prior_knowledge.startsWith('known') ? `
              <span class="px-2 py-0.5 rounded-md bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 font-semibold border border-amber-300 dark:border-amber-800" title="Число компонент смеси известно априори">
                🔒 ${TAXONOMY_LABELS.prior_knowledge[uc.prior_knowledge] || 'K фиксировано'}
              </span>
            ` : `
              <span class="px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold border border-indigo-200 dark:border-indigo-800" title="Число компонент смеси подлежит отбору">
                🔍 ${TAXONOMY_LABELS.prior_knowledge[uc.prior_knowledge] || 'K неизвестно'}
              </span>
            `}

            <!-- Axis 2: Morphology -->
            <span class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700">
              ${TAXONOMY_LABELS.component_morphology[uc.component_morphology] || uc.component_morphology}
            </span>

            <!-- Axis 4: Observation Regime -->
            <span class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700">
              ${TAXONOMY_LABELS.observation_regime[uc.observation_regime] || uc.observation_regime}
            </span>

            <!-- Axis 5: Sample Regime -->
            <span class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700">
              ${TAXONOMY_LABELS.sample_regime[uc.sample_regime] || uc.sample_regime}
            </span>
          </div>

          <!-- Category Chips Breakdown -->
          <div class="flex flex-wrap items-center gap-1 mb-3">
            ${(() => {
              const catCounts = {};
              reqs.forEach(r => {
                const pfx = r.req_id.split('-')[0];
                catCounts[pfx] = (catCounts[pfx] || 0) + 1;
              });
              return Object.entries(catCounts).map(([pfx, cnt]) => `
                <span class="px-1.5 py-0.2 rounded font-mono text-[9px] font-semibold bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700" title="Требований в группе ${pfx}">
                  ${pfx}: ${cnt}
                </span>
              `).join('');
            })()}
          </div>

          <!-- Benchmark Box -->
          <div class="bg-slate-50 dark:bg-slate-800/50 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 mb-3 text-xs flex-grow flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between text-[11px] mb-1">
                <span class="font-bold text-slate-700 dark:text-slate-300">Бенчмарк: ${primaryArt.dataset_name || 'Данные'}</span>
                <span class="px-1.5 py-0.2 font-mono text-[10px] bg-slate-200 dark:bg-slate-700 rounded text-slate-700 dark:text-slate-300 font-semibold">N = ${formatNumber(primaryArt.sample_size)}</span>
              </div>
              <div class="text-[11px] text-slate-500 dark:text-slate-400 truncate mb-1.5">
                ${primaryArt.authors ? primaryArt.authors.split(';')[0] + ' (' + primaryArt.year + ')' : ''} — ${primaryArt.title || ''}
              </div>
            </div>
            <div class="flex items-center gap-2 text-[10px] pt-1.5 border-t border-slate-200/60 dark:border-slate-700/60 flex-wrap" onclick="event.stopPropagation()">
              ${primaryArt.dataset_url ? `
                <a href="${primaryArt.dataset_url}" target="_blank" rel="noopener noreferrer" class="text-emerald-600 dark:text-emerald-400 font-semibold hover:underline flex items-center gap-0.5">
                  <span>📊</span> Датасет ↗
                </a>
              ` : (primaryArt.data_availability === 'in_paper' ? `
                <span class="text-slate-500 text-[10px]">📋 В статье</span>
              ` : '')}
              ${primaryArt.reproducibility_link && primaryArt.code_availability !== 'none' ? `
                <a href="${primaryArt.reproducibility_link}" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline flex items-center gap-0.5">
                  <span>💻</span> Код ↗
                </a>
              ` : ''}
              ${primaryArt.doi ? `
                <a href="${primaryArt.doi}" target="_blank" rel="noopener noreferrer" class="text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:underline flex items-center gap-0.5 ml-auto">
                  <span>📄</span> DOI ↗
                </a>
              ` : ''}
            </div>
          </div>

          <!-- Card Footer: Reqs count & Readiness preview -->
          <div class="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px]">
            <div class="flex items-center gap-2">
              <span class="text-rose-600 dark:text-rose-400 font-semibold" title="Критические требования">🔥 ${critReqs.length} крит.</span>
              <span class="text-slate-400 dark:text-slate-500">|</span>
              <span class="text-slate-600 dark:text-slate-400 font-medium" title="Желательные требования">✨ ${desReqs.length} жел.</span>
            </div>
            <span class="text-indigo-600 dark:text-indigo-400 font-bold hover:underline flex items-center gap-1">
              Детали сценария →
            </span>
          </div>
        `;

        el.cardsGrid.appendChild(card);
      });
    }

    // Render Matrix View
    function renderMatrix() {
      const ucs = getFilteredUseCases();
      const ecoFilter = state.filterMatrixEco;
      const q = state.searchQuery.toLowerCase().trim();
      
      const filteredTools = RAW_DATA.tools.filter(t => {
        if (ecoFilter === 'Python' && t.ecosystem !== 'Python') return false;
        if (ecoFilter === 'R' && !t.ecosystem.includes('R')) return false;
        if (ecoFilter === 'other' && (t.ecosystem.includes('R') || t.ecosystem === 'Python')) return false;
        if (q && !t.name.toLowerCase().includes(q) && !t.ecosystem.toLowerCase().includes(q)) return false;
        return true;
      });

      el.filterStatusText.innerText = `Матрица: ${filteredTools.length} библиотек × ${ucs.length} сценариев`;

      const sortedTools = [...filteredTools].sort((a, b) => {
        if (a.tool_id === 'pysatl-mpest') return -1;
        if (b.tool_id === 'pysatl-mpest') return 1;
        return (RAW_DATA.tool_avg_readiness[b.tool_id] || 0) - (RAW_DATA.tool_avg_readiness[a.tool_id] || 0);
      });

      let html = `
        <thead>
          <tr class="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700">
            <th class="p-2.5 font-bold sticky-header-corner bg-slate-100 dark:bg-slate-800 min-w-[200px] border-r border-slate-200 dark:border-slate-700">
              Библиотека / Пакет (${sortedTools.length})
            </th>
            <th class="p-2.5 font-bold sticky-th text-center min-w-[70px] bg-slate-100 dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700" title="Средняя готовность по всем 10 сценариям">
              Среднее
            </th>
      `;

      ucs.forEach(uc => {
        html += `
          <th class="p-2 font-bold sticky-th text-center min-w-[95px] bg-slate-100 dark:bg-slate-800 cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700 border-r border-slate-200 dark:border-slate-700" onclick="openDrawer('${uc.usecase_id}')" title="${uc.name} (${uc.domain})">
            <div class="text-[10px] text-indigo-600 dark:text-indigo-400 font-black">${uc.usecase_id}</div>
            <div class="truncate text-[10px] font-medium text-slate-600 dark:text-slate-300 max-w-[85px] mx-auto">${uc.domain.split(' ')[0]}</div>
          </th>
        `;
      });

      html += `</tr></thead><tbody>`;

      sortedTools.forEach(t => {
        const isTarget = t.tool_id === 'pysatl-mpest';
        const avgScore = RAW_DATA.tool_avg_readiness[t.tool_id] || 0;
        const rowClass = isTarget 
          ? 'bg-indigo-50/70 dark:bg-indigo-950/40 font-bold border-b-2 border-indigo-500' 
          : 'border-b border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50';

        html += `
          <tr class="${rowClass}">
            <td class="p-2.5 sticky-col-1 ${isTarget ? 'bg-indigo-50 dark:bg-slate-900 font-bold text-indigo-900 dark:text-indigo-300' : 'bg-white dark:bg-slate-900'} border-r border-slate-200 dark:border-slate-800">
              <div class="flex items-center gap-1.5">
                <span class="truncate">${t.name}</span>
                <span class="text-[10px] text-slate-400 font-normal">(${t.ecosystem})</span>
              </div>
            </td>
            <td class="p-2 text-center font-bold font-mono border-r border-slate-200 dark:border-slate-800 ${avgScore >= 70 ? 'text-emerald-600 dark:text-emerald-400' : (avgScore >= 50 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-500')}">
              ${avgScore}%
            </td>
        `;

        ucs.forEach(uc => {
          const res = RAW_DATA.readiness_matrix[t.tool_id]?.[uc.usecase_id] || { score: 0, critical_ok: false };
          const cellBadge = getReadinessClass(res.score, res.critical_ok);
          const flag = res.critical_ok ? '✓' : '⚠';

          html += `
            <td class="p-1.5 text-center border-r border-slate-200 dark:border-slate-800">
              <span class="inline-flex items-center justify-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-mono font-bold border ${cellBadge} cursor-pointer hover:scale-105 transition" onclick="openDrawer('${uc.usecase_id}')" title="${t.name} в ${uc.usecase_id}: ${res.score}% (${res.critical_ok ? 'Все крит. требования выполнены' : 'Не хватает крит. требований'}) — кликните для деталей">
                <span>${res.score}%</span>
                <span class="text-[9px] ${res.critical_ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${flag}</span>
              </span>
            </td>
          `;
        });

        html += `</tr>`;
      });

      html += `</tbody>`;
      el.tableMatrix.innerHTML = html;
    }

    // Render Audit View
    function renderAudit() {
      const q = state.searchQuery.toLowerCase().trim();
      const allArts = [];
      Object.entries(RAW_DATA.usecase_articles).forEach(([uid, arts]) => {
        arts.forEach(a => {
          allArts.push({ ...a, usecase_id: uid });
        });
      });

      const filteredArts = allArts.filter(a => {
        if (state.filterDomain !== 'all') {
          const uc = RAW_DATA.usecases.find(u => u.usecase_id === a.usecase_id);
          if (uc && uc.domain !== state.filterDomain) return false;
        }
        if (q) {
          const inTitle = a.title && a.title.toLowerCase().includes(q);
          const inAuthors = a.authors && a.authors.toLowerCase().includes(q);
          const inDs = a.dataset_name && a.dataset_name.toLowerCase().includes(q);
          const inId = a.article_id && a.article_id.toLowerCase().includes(q);
          const inUc = a.usecase_id && a.usecase_id.toLowerCase().includes(q);
          if (!inTitle && !inAuthors && !inDs && !inId && !inUc) return false;
        }
        return true;
      });

      el.filterStatusText.innerText = `Аудит: ${filteredArts.length} бенчмарков`;

      let fullCount = allArts.filter(a => a.reproducibility_link && a.code_availability !== 'none' && (a.dataset_url || a.data_availability === 'open')).length;
      let dataCount = allArts.filter(a => a.dataset_url || a.data_availability === 'open' || a.data_availability === 'in_paper').length;

      document.getElementById('audit-stat-full').innerText = `${fullCount} бенчмарков`;
      document.getElementById('audit-stat-data').innerText = `${dataCount} бенчмарков`;

      let html = `
        <thead>
          <tr class="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700">
            <th class="p-2.5 font-bold sticky-th">Сценарий</th>
            <th class="p-2.5 font-bold sticky-th">Бенчмарк / Датасет</th>
            <th class="p-2.5 font-bold sticky-th">Объем (N)</th>
            <th class="p-2.5 font-bold sticky-th">Доступность данных и кода</th>
            <th class="p-2.5 font-bold sticky-th">Научная публикация</th>
            <th class="p-2.5 font-bold sticky-th">Прямые ссылки (Датасет / Код)</th>
          </tr>
        </thead>
        <tbody>
      `;

      filteredArts.forEach(a => {
        const hasCode = a.reproducibility_link && a.code_availability !== 'none';
        const hasOpenData = !!a.dataset_url || a.data_availability === 'open';
        const isDataInPaper = a.data_availability === 'in_paper';

        let repClass = 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300';
        let repLabel = 'Данные закрыты';

        if (hasCode && hasOpenData) {
          repClass = 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border-emerald-300';
          repLabel = 'Полная (код + данные)';
        } else if (hasOpenData) {
          repClass = 'bg-sky-100 dark:bg-sky-950 text-sky-800 dark:text-sky-300 border-sky-300';
          repLabel = 'Открытый датасет';
        } else if (isDataInPaper) {
          repClass = 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border-amber-300';
          repLabel = 'Данные в тексте статьи';
        }

        html += `
          <tr class="border-b border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
            <td class="p-2.5 font-bold text-indigo-600 dark:text-indigo-400">
              <span class="cursor-pointer hover:underline" onclick="openDrawer('${a.usecase_id}')">${a.usecase_id}</span>
            </td>
            <td class="p-2.5 font-semibold text-slate-800 dark:text-slate-200">
              ${a.dataset_name}
            </td>
            <td class="p-2.5 font-mono text-slate-600 dark:text-slate-400">
              ${formatNumber(a.sample_size)}
            </td>
            <td class="p-2.5">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${repClass}">
                ${repLabel}
              </span>
            </td>
            <td class="p-2.5 max-w-md">
              <div class="font-medium text-slate-900 dark:text-slate-100 flex items-start justify-between gap-1.5">
                <span>${a.title}</span>
                ${a.doi ? `
                  <a href="${a.doi}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-indigo-600 shrink-0 text-xs font-mono" title="Открыть DOI публикации">
                    DOI ↗
                  </a>
                ` : ''}
              </div>
              <div class="text-[11px] text-slate-500 dark:text-slate-400">${a.authors} (${a.year})</div>
            </td>
            <td class="p-2.5">
              <div class="flex items-center gap-2 flex-wrap text-[11px]">
                ${a.dataset_url ? `
                  <a href="${a.dataset_url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 hover:underline font-semibold">
                    <span>📊</span> Датасет ↗
                  </a>
                ` : (isDataInPaper ? `
                  <span class="text-slate-400 text-[10px]">📋 В таблицах статьи</span>
                ` : '')}
                ${hasCode ? `
                  <a href="${a.reproducibility_link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">
                    <span>💻</span> Код ↗
                  </a>
                ` : ''}
                ${!a.dataset_url && !hasCode && !isDataInPaper ? '<span class="text-slate-400 text-xs">—</span>' : ''}
              </div>
            </td>
          </tr>
        `;
      });

      html += `</tbody>`;
      el.tableAudit.innerHTML = html;
    }

    // Drawer Open & Close Functions
    function openDrawer(ucId) {
      const uc = RAW_DATA.usecases.find(x => x.usecase_id === ucId);
      if (!uc) return;

      state.selectedUseCaseId = ucId;
      state.showAllRankings = false;
      el.btnToggleAllRankings.innerText = 'Показать все 27';

      el.drawerUcId.innerText = uc.usecase_id;
      el.drawerUcDomain.innerText = uc.domain;
      el.drawerUcName.innerText = uc.name;
      el.drawerUcDesc.innerText = uc.description;

      // Render Taxonomy Grid
      el.drawerTaxonomyGrid.innerHTML = `
        <div class="bg-slate-100 dark:bg-slate-800/80 p-2 rounded border border-slate-200 dark:border-slate-700">
          <div class="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold">Тип смеси</div>
          <div class="font-semibold text-slate-800 dark:text-slate-200">${TAXONOMY_LABELS.mixture_type[uc.mixture_type] || uc.mixture_type}</div>
        </div>
        <div class="bg-slate-100 dark:bg-slate-800/80 p-2 rounded border border-slate-200 dark:border-slate-700">
          <div class="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold">Число компонент (K)</div>
          <div class="font-semibold ${uc.prior_knowledge && uc.prior_knowledge.startsWith('known') ? 'text-amber-600 dark:text-amber-400 font-bold' : 'text-indigo-600 dark:text-indigo-400 font-bold'}">${TAXONOMY_LABELS.prior_knowledge[uc.prior_knowledge] || uc.prior_knowledge}</div>
        </div>
        <div class="bg-slate-100 dark:bg-slate-800/80 p-2 rounded border border-slate-200 dark:border-slate-700">
          <div class="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold">Морфология</div>
          <div class="font-semibold text-slate-800 dark:text-slate-200">${TAXONOMY_LABELS.component_morphology[uc.component_morphology] || uc.component_morphology}</div>
        </div>
        <div class="bg-slate-100 dark:bg-slate-800/80 p-2 rounded border border-slate-200 dark:border-slate-700">
          <div class="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold">Режим наблюдения</div>
          <div class="font-semibold text-slate-800 dark:text-slate-200">${TAXONOMY_LABELS.observation_regime[uc.observation_regime] || uc.observation_regime}</div>
        </div>
        <div class="bg-slate-100 dark:bg-slate-800/80 p-2 rounded border border-slate-200 dark:border-slate-700 col-span-2">
          <div class="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold">Масштаб выборки</div>
          <div class="font-semibold text-slate-800 dark:text-slate-200">${TAXONOMY_LABELS.sample_regime[uc.sample_regime] || uc.sample_regime}</div>
        </div>
      `;

      // Render Requirements (with category grouping support)
      const reqs = RAW_DATA.usecase_requirements[ucId] || [];
      el.drawerReqsCount.innerText = `${reqs.length} требований`;
      renderDrawerRequirementsList(reqs);

      // Render Articles
      const arts = RAW_DATA.usecase_articles[ucId] || [];
      el.drawerArticlesCount.innerText = `${arts.length} публикаций`;
      el.drawerArticlesList.innerHTML = arts.map(a => {
        const roleLabel = a.case_role === 'primary_benchmark' ? 'Первичный бенчмарк' : (a.case_role === 'validation' ? 'Валидация' : 'Применение');
        const roleClass = a.case_role === 'primary_benchmark' 
          ? 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border-amber-300'
          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300';

        const dataBadgeOrLink = a.dataset_url ? `
          <a href="${a.dataset_url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 hover:underline font-semibold">
            <span>📊</span> Открытый датасет →
          </a>
        ` : (a.data_availability === 'in_paper' ? `
          <span class="inline-flex items-center gap-1 text-slate-500 dark:text-slate-400 text-[10px] font-medium bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded">
            <span>📋</span> Данные в таблицах статьи
          </span>
        ` : '');

        const codeLink = (a.reproducibility_link && a.code_availability !== 'none') ? `
          <a href="${a.reproducibility_link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">
            <span>💻</span> Репозиторий кода →
          </a>
        ` : '';

        const doiLink = a.doi ? `
          <a href="${a.doi}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-slate-600 dark:text-slate-400 hover:underline">
            <span>📄</span> DOI статьи →
          </a>
        ` : '';

        return `
          <div class="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40">
            <div class="flex items-center justify-between gap-2 mb-1">
              <span class="font-bold text-slate-900 dark:text-slate-100">${a.dataset_name} (N = ${formatNumber(a.sample_size)})</span>
              <span class="px-1.5 py-0.5 text-[10px] font-bold rounded border ${roleClass}">${roleLabel}</span>
            </div>
            <div class="text-[11px] text-slate-600 dark:text-slate-300 font-medium mb-1">
              ${a.title}
            </div>
            <div class="text-[10px] text-slate-500 dark:text-slate-400 mb-1.5">
              ${a.authors} (${a.year})
            </div>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 italic mb-2">
              ${a.case_note}
            </p>
            <div class="flex items-center gap-3 text-[11px] flex-wrap pt-1.5 border-t border-slate-200 dark:border-slate-800">
              ${dataBadgeOrLink}
              ${codeLink}
              ${doiLink}
            </div>
          </div>
        `;
      }).join('');

      renderDrawerRankings(ucId);

      // Open drawer animation with inline style fallback
      el.drawerBackdrop.classList.remove('hidden');
      requestAnimationFrame(() => {
        el.drawerBackdrop.classList.remove('opacity-0');
        el.drawerBackdrop.classList.add('opacity-100');
        el.drawer.classList.remove('is-closed');
        el.drawer.classList.add('is-open');
        el.drawer.style.transform = 'translateX(0)';
      });
    }

        function renderSingleReqCard(r) {
      const isCrit = r.importance === 'critical';
      const impBadge = isCrit
        ? '<span class="px-1.5 py-0.5 text-[10px] font-bold rounded border bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border-rose-300">Критическое</span>'
        : '<span class="px-1.5 py-0.5 text-[10px] font-bold rounded border bg-sky-100 dark:bg-sky-950 text-sky-800 dark:text-sky-300 border-sky-300">Желательное</span>';

      const prioClass = r.priority === 'must'
        ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200'
        : (r.priority === 'should'
          ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200'
          : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-200');

      const prioBadge = r.priority
        ? `<span class="px-1.5 py-0.2 text-[9px] font-bold uppercase rounded border ${prioClass}">${r.priority}</span>`
        : '';

      const supportText = r.tools_supported_count !== undefined
        ? `<span class="text-[10px] text-slate-400 dark:text-slate-500 font-mono" title="Число пакетов с поддержкой фичи">Библиотек: ${r.tools_supported_count}/${r.tools_supported_total}</span>`
        : '';

      return `
        <div class="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800/70 hover:border-indigo-300 dark:hover:border-indigo-700 transition">
          <div class="flex items-center justify-between gap-2 mb-1.5 flex-wrap">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="font-mono font-bold text-indigo-600 dark:text-indigo-400 text-xs">${r.req_id}</span>
              <span class="font-semibold text-slate-900 dark:text-slate-100 text-xs">${r.req_name || ''}</span>
              ${prioBadge}
            </div>
            <div class="flex items-center gap-2">
              ${supportText}
              ${impBadge}
            </div>
          </div>
          <p class="text-slate-600 dark:text-slate-300 leading-relaxed text-justify text-[11px]">
            ${r.rationale}
          </p>
        </div>
      `;
    }

    function renderDrawerRequirementsList(reqs) {
      if (!reqs || reqs.length === 0) {
        el.drawerReqsList.innerHTML = '<div class="text-slate-400 text-center py-4">Нет привязанных требований</div>';
        return;
      }

      if (state.drawerReqsGrouping === 'importance') {
        // Flat sorted by critical first
        const sorted = [...reqs].sort((a, b) => {
          if (a.importance === 'critical' && b.importance !== 'critical') return -1;
          if (a.importance !== 'critical' && b.importance === 'critical') return 1;
          return a.req_id.localeCompare(b.req_id);
        });
        el.drawerReqsList.innerHTML = sorted.map(r => renderSingleReqCard(r)).join('');
        return;
      }

      // Group by Category matching dashboard.html
      const grouped = {};
      reqs.forEach(r => {
        const cat = r.req_type || (r.req_id.split('-')[0].toLowerCase() === 'est' ? 'estimation' : 'other');
        grouped[cat] = grouped[cat] || [];
        grouped[cat].push(r);
      });

      let html = '';
      CATEGORY_ORDER.forEach(catKey => {
        const catReqs = grouped[catKey];
        if (!catReqs || catReqs.length === 0) return;
        
        // Sort inside category: critical first
        catReqs.sort((a, b) => {
          if (a.importance === 'critical' && b.importance !== 'critical') return -1;
          if (a.importance !== 'critical' && b.importance === 'critical') return 1;
          return a.req_id.localeCompare(b.req_id);
        });

        const meta = CATEGORY_META[catKey] || { title: catKey, icon: '📁', prefix: catKey.toUpperCase() };
        const critCount = catReqs.filter(r => r.importance === 'critical').length;
        const desCount = catReqs.filter(r => r.importance === 'desirable').length;

        html += `
          <div class="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-50/50 dark:bg-slate-900/40 shadow-sm">
            <div class="px-3 py-2 bg-slate-200/70 dark:bg-slate-800 border-b border-slate-300 dark:border-slate-700 flex items-center justify-between text-xs select-none">
              <div class="flex items-center gap-1.5 font-bold text-slate-800 dark:text-slate-100">
                <span>${meta.icon}</span>
                <span>${meta.title}</span>
                <span class="text-[11px] text-slate-500 font-normal">(${catReqs.length})</span>
              </div>
              <div class="flex items-center gap-1 text-[10px]">
                ${critCount > 0 ? `<span class="px-1.5 py-0.2 rounded font-bold bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300 border border-rose-300 dark:border-rose-900">${critCount} крит.</span>` : ''}
                ${desCount > 0 ? `<span class="px-1.5 py-0.2 rounded font-bold bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 border border-sky-300 dark:border-sky-900">${desCount} жел.</span>` : ''}
              </div>
            </div>
            <div class="p-2 space-y-2">
              ${catReqs.map(r => renderSingleReqCard(r)).join('')}
            </div>
          </div>
        `;
      });

      // Handle any categories not in CATEGORY_ORDER
      Object.keys(grouped).forEach(catKey => {
        if (!CATEGORY_ORDER.includes(catKey)) {
          const catReqs = grouped[catKey];
          html += `
            <div class="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-50/50 dark:bg-slate-900/40 p-2 space-y-2">
              <div class="font-bold text-xs px-1 text-slate-700 dark:text-slate-300">${catKey} (${catReqs.length})</div>
              ${catReqs.map(r => renderSingleReqCard(r)).join('')}
            </div>
          `;
        }
      });

      el.drawerReqsList.innerHTML = html;
    }

    function renderDrawerRankings(ucId) {
      const rankings = Object.entries(RAW_DATA.readiness_matrix).map(([tid, ucs]) => {
        const t = RAW_DATA.tools.find(x => x.tool_id === tid);
        return {
          tid,
          name: t ? t.name : tid,
          ecosystem: t ? t.ecosystem : '',
          score: ucs[ucId] ? ucs[ucId].score : 0,
          critical_ok: ucs[ucId] ? ucs[ucId].critical_ok : false
        };
      }).sort((a, b) => b.score - a.score);

      const items = state.showAllRankings ? rankings : rankings.slice(0, 10);

      el.drawerReadinessRanking.innerHTML = items.map((r, i) => {
        const isTarget = r.tid === 'pysatl-mpest';
        const badge = getReadinessClass(r.score, r.critical_ok);
        return `
          <div class="flex items-center justify-between py-1 px-2 rounded ${isTarget ? 'bg-indigo-100 dark:bg-indigo-950 font-bold border border-indigo-300' : ''}">
            <div class="flex items-center gap-2">
              <span class="w-4 text-slate-400 font-mono text-[10px]">${i + 1}.</span>
              <span class="${isTarget ? 'text-indigo-900 dark:text-indigo-200' : 'text-slate-700 dark:text-slate-300'}">${r.name}</span>
              <span class="text-[10px] text-slate-400 font-normal">(${r.ecosystem})</span>
            </div>
            <span class="px-2 py-0.5 rounded text-[11px] font-mono font-bold border ${badge}">
              ${r.score}% ${r.critical_ok ? '✓' : '⚠'}
            </span>
          </div>
        `;
      }).join('');
    }

    function closeDrawer() {
      el.drawer.classList.remove('is-open');
      el.drawer.classList.add('is-closed');
      el.drawer.style.transform = 'translateX(100%)';
      el.drawerBackdrop.classList.remove('opacity-100');
      el.drawerBackdrop.classList.add('opacity-0');
      setTimeout(() => {
        el.drawerBackdrop.classList.add('hidden');
      }, 300);
    }

    // Attach to window so onclick in HTML always works
    window.openDrawer = openDrawer;
    window.closeDrawer = closeDrawer;

        el.btnGroupByCat.addEventListener('click', () => {
      state.drawerReqsGrouping = 'category';
      el.btnGroupByCat.className = 'px-2 py-0.5 rounded font-semibold text-indigo-700 dark:text-indigo-300 bg-white dark:bg-slate-900 shadow-sm transition';
      el.btnGroupByImp.className = 'px-2 py-0.5 rounded font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition';
      if (state.selectedUseCaseId) {
        renderDrawerRequirementsList(RAW_DATA.usecase_requirements[state.selectedUseCaseId] || []);
      }
    });

    el.btnGroupByImp.addEventListener('click', () => {
      state.drawerReqsGrouping = 'importance';
      el.btnGroupByImp.className = 'px-2 py-0.5 rounded font-semibold text-indigo-700 dark:text-indigo-300 bg-white dark:bg-slate-900 shadow-sm transition';
      el.btnGroupByCat.className = 'px-2 py-0.5 rounded font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition';
      if (state.selectedUseCaseId) {
        renderDrawerRequirementsList(RAW_DATA.usecase_requirements[state.selectedUseCaseId] || []);
      }
    });

    el.btnToggleAllRankings.addEventListener('click', () => {
      state.showAllRankings = !state.showAllRankings;
      el.btnToggleAllRankings.innerText = state.showAllRankings ? 'Свернуть до 10' : 'Показать все 27';
      if (state.selectedUseCaseId) {
        renderDrawerRankings(state.selectedUseCaseId);
      }
    });

    // Switch View Tabs
    function setView(viewName) {
      state.activeView = viewName;
      
      [el.tabCards, el.tabMatrix, el.tabAudit].forEach(btn => {
        btn.classList.remove('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
        btn.classList.add('text-slate-600', 'dark:text-slate-300');
      });

      el.viewCards.classList.add('hidden');
      el.viewMatrix.classList.add('hidden');
      el.viewAudit.classList.add('hidden');

      if (viewName === 'cards') {
        el.tabCards.classList.add('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
        el.tabCards.classList.remove('text-slate-600', 'dark:text-slate-300');
        el.viewCards.classList.remove('hidden');
        renderCards();
      } else if (viewName === 'matrix') {
        el.tabMatrix.classList.add('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
        el.tabMatrix.classList.remove('text-slate-600', 'dark:text-slate-300');
        el.viewMatrix.classList.remove('hidden');
        renderMatrix();
      } else if (viewName === 'audit') {
        el.tabAudit.classList.add('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
        el.tabAudit.classList.remove('text-slate-600', 'dark:text-slate-300');
        el.viewAudit.classList.remove('hidden');
        renderAudit();
      }
    }

    // Refresh active view
    function updateActiveView() {
      if (state.activeView === 'cards') renderCards();
      else if (state.activeView === 'matrix') renderMatrix();
      else if (state.activeView === 'audit') renderAudit();
    }

    // Event Listeners
    el.tabCards.addEventListener('click', () => setView('cards'));
    el.tabMatrix.addEventListener('click', () => setView('matrix'));
    el.tabAudit.addEventListener('click', () => setView('audit'));

    el.inputSearch.addEventListener('input', e => {
      state.searchQuery = e.target.value;
      updateActiveView();
    });

    el.filterDomain.addEventListener('change', e => {
      state.filterDomain = e.target.value;
      updateActiveView();
    });

    el.filterMixtureType.addEventListener('change', e => {
      state.filterMixtureType = e.target.value;
      updateActiveView();
    });

    el.filterMorphology.addEventListener('change', e => {
      state.filterMorphology = e.target.value;
      updateActiveView();
    });

    el.filterPriorKnowledge.addEventListener('change', e => {
      state.filterPriorKnowledge = e.target.value;
      updateActiveView();
    });

    el.filterObservationRegime.addEventListener('change', e => {
      state.filterObservationRegime = e.target.value;
      updateActiveView();
    });

    el.filterSampleRegime.addEventListener('change', e => {
      state.filterSampleRegime = e.target.value;
      updateActiveView();
    });

    el.btnResetFilters.addEventListener('click', () => {
      state.searchQuery = '';
      state.filterDomain = 'all';
      state.filterMixtureType = 'all';
      state.filterMorphology = 'all';
      state.filterPriorKnowledge = 'all';
      state.filterObservationRegime = 'all';
      state.filterSampleRegime = 'all';
      state.filterMatrixEco = 'all';

      el.inputSearch.value = '';
      el.filterDomain.value = 'all';
      el.filterMixtureType.value = 'all';
      el.filterMorphology.value = 'all';
      el.filterPriorKnowledge.value = 'all';
      el.filterObservationRegime.value = 'all';
      el.filterSampleRegime.value = 'all';

      document.querySelectorAll('.matrix-eco-btn').forEach(b => {
        b.classList.remove('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
        b.classList.add('text-slate-600', 'dark:text-slate-300');
        if (b.dataset.matrixEco === 'all') {
          b.classList.add('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
          b.classList.remove('text-slate-600', 'dark:text-slate-300');
        }
      });

      updateActiveView();
    });

    // Matrix ecosystem filter buttons
    document.querySelectorAll('.matrix-eco-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.matrix-eco-btn').forEach(b => {
          b.classList.remove('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
          b.classList.add('text-slate-600', 'dark:text-slate-300');
        });
        btn.classList.add('bg-indigo-50', 'dark:bg-indigo-950/70', 'text-indigo-700', 'dark:text-indigo-300');
        btn.classList.remove('text-slate-600', 'dark:text-slate-300');
        state.filterMatrixEco = btn.dataset.matrixEco;
        renderMatrix();
      });
    });

    // Drawer close events
    el.btnCloseDrawer.addEventListener('click', closeDrawer);
    el.drawerBackdrop.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeDrawer();
    });

    // Theme toggle
    el.btnThemeToggle.addEventListener('click', () => {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.theme = isDark ? 'dark' : 'light';
      el.themeToggleIcon.innerText = isDark ? '☀️' : '🌙';
      el.themeToggleText.innerText = isDark ? 'Светлая' : 'Темная';
    });

    // Init Theme button text
    if (document.documentElement.classList.contains('dark')) {
      el.themeToggleIcon.innerText = '☀️';
      el.themeToggleText.innerText = 'Светлая';
    } else {
      el.themeToggleIcon.innerText = '🌙';
      el.themeToggleText.innerText = 'Темная';
    }

    // Initial render
    setView('cards');
  </script>
</body>
</html>
"""


def generate_usecases_dashboard(data_dir: Path, output_file: Path):

    # Load tools
    with open(data_dir / "reqs" / "tools.csv", encoding="utf-8") as f:
        tools = list(csv.DictReader(f))

    # Load requirements
    with open(data_dir / "requirements.csv", encoding="utf-8") as f:
        requirements = list(csv.DictReader(f))
    req_dict = {r["req_id"]: r for r in requirements}

    # Load evaluations
    with open(data_dir / "reqs" / "evaluations.csv", encoding="utf-8") as f:
        evaluations = list(csv.DictReader(f))
    eval_lookup = {(e["tool_id"], e["req_id"]): e["status"] for e in evaluations}

    # Load articles
    with open(data_dir / "articles.csv", encoding="utf-8") as f:
        articles = list(csv.DictReader(f))
    art_dict = {a["article_id"]: a for a in articles}

    # Load use cases
    with open(data_dir / "usecases" / "usecases.csv", encoding="utf-8") as f:
        usecases = list(csv.DictReader(f))

    # Load use case articles
    with open(data_dir / "usecases" / "usecase_articles.csv", encoding="utf-8") as f:
        usecase_articles = list(csv.DictReader(f))

    # Load use case requirements
    with open(data_dir / "usecases" / "usecase_requirements.csv", encoding="utf-8") as f:
        usecase_requirements = list(csv.DictReader(f))

    # Compute readiness scores
    status_weight = {"yes": 1.0, "partial": 0.5, "no": 0.0}
    imp_weight = {"critical": 2.0, "desirable": 1.0}

    # Group reqs by UC
    uc_reqs_map = {}
    for ur in usecase_requirements:
        item = dict(ur)
        req_meta = req_dict.get(ur["req_id"], {})
        item["req_name"] = req_meta.get("name", "")
        item["req_type"] = req_meta.get("type", "")
        item["priority"] = req_meta.get("priority", "")
        supported = [t["name"] for t in tools if eval_lookup.get((t["tool_id"], ur["req_id"])) in {"yes", "partial"}]
        item["tools_supported_count"] = len(supported)
        item["tools_supported_total"] = len(tools)
        uc_reqs_map.setdefault(ur["usecase_id"], []).append(item)

    # Group arts by UC
    uc_arts_map = {}
    for ua in usecase_articles:
        art = art_dict.get(ua["article_id"], {})
        item = dict(ua)
        item["title"] = art.get("title", "")
        item["authors"] = art.get("authors", "")
        item["year"] = art.get("year", "")
        item["doi"] = art.get("doi", "")
        item["url"] = art.get("url", "")
        item["reproducibility_status"] = art.get("reproducibility_status", "not_applicable")
        item["data_availability"] = art.get("data_availability", "not_applicable")
        item["code_availability"] = art.get("code_availability", "not_applicable")
        item["reproducibility_link"] = art.get("reproducibility_link", "")
        item["dataset_url"] = ua.get("dataset_url", "")
        uc_arts_map.setdefault(ua["usecase_id"], []).append(item)

    # Build readiness matrix
    readiness_matrix = {}
    tool_avg_readiness = {}

    for t in tools:
        tid = t["tool_id"]
        readiness_matrix[tid] = {}
        total_score = 0.0
        for uc in usecases:
            uid = uc["usecase_id"]
            r_list = uc_reqs_map.get(uid, [])
            max_score = sum(imp_weight[r["importance"]] for r in r_list)
            if max_score > 0:
                cur_score = sum(imp_weight[r["importance"]] * status_weight[eval_lookup.get((tid, r["req_id"]), "no")] for r in r_list)
                pct = round((cur_score / max_score) * 100, 1)
                crit_ok = all(eval_lookup.get((tid, r["req_id"]), "no") in {"yes", "partial"} for r in r_list if r["importance"] == "critical")
            else:
                pct = 0.0
                crit_ok = True
            readiness_matrix[tid][uid] = {
                "score": pct,
                "critical_ok": crit_ok
            }
            total_score += pct
        tool_avg_readiness[tid] = round(total_score / len(usecases), 1)

    payload = {
        "usecases": usecases,
        "usecase_articles": uc_arts_map,
        "usecase_requirements": uc_reqs_map,
        "tools": tools,
        "readiness_matrix": readiness_matrix,
        "tool_avg_readiness": tool_avg_readiness
    }

    raw_json = json.dumps(payload, ensure_ascii=False)
    html_content = USECASES_HTML_TEMPLATE.replace("__RAW_USECASES_DATA__", raw_json)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Дашборд юзкейсов успешно сгенерирован: {output_file} ({output_file.stat().st_size / 1024:.1f} KB)")




def parse_args():
    parser = argparse.ArgumentParser(
        description="Генератор интерактивных HTML-дашбордов анализа требований, литературы и прикладных юзкейсов."
    )
    parser.add_argument(
        "--data-dir", "-d",
        type=Path,
        default=Path("articles/raw"),
        help="Путь к каталогу с сырыми CSV-таблицами (по умолчанию: articles/raw)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("articles/dashboard.html"),
        help="Путь к результирующему HTML-файлу матрицы требований (по умолчанию: articles/dashboard.html)",
    )
    parser.add_argument(
        "--usecases-output", "-u",
        type=Path,
        default=Path("articles/usecases_dashboard.html"),
        help="Путь к результирующему HTML-файлу дашборда юзкейсов (по умолчанию: articles/usecases_dashboard.html)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_dashboard(args.data_dir, args.output)
    if (args.data_dir / "usecases").exists():
        generate_usecases_dashboard(args.data_dir, args.usecases_output)
