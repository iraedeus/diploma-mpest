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
    tools_path = data_dir / "tools.csv"
    reqs_path = data_dir / "requirements.csv"
    evals_path = data_dir / "evaluations.csv"
    arts_path = data_dir / "articles.csv"
    req_arts_path = data_dir / "requirement_articles.csv"

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Генератор интерактивного HTML-дашборда анализа требований и литературы по смесям распределений."
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
        help="Путь к результирующему HTML-файлу (по умолчанию: articles/dashboard.html)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_dashboard(args.data_dir, args.output)
