# Журнал поисковых запросов

Журнал документирует первоначальный поиск литературы по конечным смесям одномерных непрерывных распределений. Актуальные критерии и результаты перескрининга описаны в [SELECTION.md](SELECTION.md); численность старых статусов ниже относится к первоначальному проходу.

## 1. Сводка по источникам и охвату

- **Дата проведения поиска:** 2026-10-09
- **Основные базы:** OpenAlex API, CrossRef, arXiv, Project Euclid, The R Journal, Journal of Statistical Software (JSS), INRIA HAL.
- **Всего поисковых запросов:** 81 (Этап I: 54, Этап II: 14, Этап III: 13)
- **Всего обнаружено уникальных работ в реестре:** 427
- **Предметная область:** Строго конечные смеси одномерных непрерывных распределений (1D Continuous FMM) и ML-модели определения их структуры.

## 2. Протокол запросов Этапа I (Широкий и направленный поиск)

| № | Направление | Источник | Поисковый запрос / путь | Глубина и сортировка | Всего в базе | Новых в каталог |
|---|---|---|---|---|---|---|
| 1 | General | OpenAlex | `finite mixture models` | top 15 (relevance) | 445420 | 15 |
| 2 | General | OpenAlex | `univariate mixture distributions` | top 15 (relevance) | 77194 | 15 |
| 3 | General | OpenAlex | `finite mixtures of continuous distributions` | top 15 (relevance) | 230548 | 13 |
| 4 | Foundations | OpenAlex | `identifiability of finite mixtures` | top 10 (relevance) | 26626 | 10 |
| 5 | Foundations | OpenAlex | `maximum likelihood from incomplete data via EM algorithm` | top 5 (relevance) | 49183 | 5 |
| 6 | Estimation | OpenAlex | `finite mixture parameter estimation` | top 15 (relevance) | 171716 | 13 |
| 7 | Estimation | OpenAlex | `mixture maximum likelihood EM` | top 10 (relevance) | 85753 | 9 |
| 8 | Estimation | OpenAlex | `mixture method of moments` | top 15 (relevance) | 213902 | 12 |
| 9 | Estimation | OpenAlex | `direct mixture estimation quasi-newton` | top 15 (relevance) | 8912 | 15 |
| 10 | Estimation | OpenAlex | `minimum distance estimation finite mixture` | top 15 (relevance) | 71447 | 13 |
| 11 | Estimation | OpenAlex | `minimum Hellinger distance finite mixture` | top 10 (relevance) | 1741 | 3 |
| 12 | Estimation | OpenAlex | `split and merge EM algorithm mixture` | top 10 (relevance) | 11546 | 7 |
| 13 | Estimation | OpenAlex | `ECME finite mixtures` | top 10 (relevance) | 227 | 9 |
| 14 | Estimation | OpenAlex | `Bayesian analysis of mixtures reversible jump MCMC` | top 10 (relevance) | 3379 | 9 |
| 15 | Initialization | OpenAlex | `finite mixture initialization` | top 15 (relevance) | 313504 | 10 |
| 16 | Initialization | OpenAlex | `EM starting values finite mixtures` | top 15 (relevance) | 41558 | 10 |
| 17 | Initialization | OpenAlex | `Choosing starting values for the EM algorithm` | top 10 (relevance) | 133426 | 10 |
| 18 | Initialization | OpenAlex | `mixture initial parameter estimation` | top 10 (relevance) | 503376 | 7 |
| 19 | Initialization | OpenAlex | `k-means initialization finite mixture EM` | top 10 (relevance) | 35432 | 7 |
| 20 | Initialization | OpenAlex | `moment based initialization finite mixtures` | top 10 (relevance) | 85077 | 5 |
| 21 | Structure-K | OpenAlex | `mixture order estimation` | top 15 (relevance) | 752463 | 13 |
| 22 | Structure-K | OpenAlex | `number of mixture components model selection` | top 15 (relevance) | 835317 | 15 |
| 23 | Structure-K | OpenAlex | `integrated completed likelihood finite mixture` | top 10 (relevance) | 32800 | 7 |
| 24 | Structure-K | OpenAlex | `consistent estimation order mixture models BIC` | top 10 (relevance) | 17813 | 8 |
| 25 | Structure-K | OpenAlex | `bootstrap likelihood ratio test mixture components` | top 10 (relevance) | 27998 | 9 |
| 26 | Structure-K | OpenAlex | `penalized likelihood finite mixture components` | top 10 (relevance) | 13658 | 8 |
| 27 | Structure-Family | OpenAlex | `heterogeneous mixture distributions` | top 15 (relevance) | 524147 | 13 |
| 28 | Structure-Family | OpenAlex | `mixed-family finite mixtures` | top 15 (relevance) | 63778 | 11 |
| 29 | Structure-Family | OpenAlex | `component family selection finite mixture` | top 15 (relevance) | 59885 | 10 |
| 30 | Structure-Family | OpenAlex | `univariate mixture different distribution families` | top 15 (relevance) | 36101 | 14 |
| 31 | Structure-Family | OpenAlex | `finite mixture Weibull Gamma Normal` | top 15 (relevance) | 3767 | 12 |
| 32 | Structure-Family | OpenAlex | `selection of mixture component distributions` | top 15 (relevance) | 743350 | 9 |
| 33 | Structure-Family | OpenAlex | `FlexMix finite mixture models R` | top 10 (relevance) | 638 | 6 |
| 34 | Foundations | OpenAlex | `Contributions to the Mathematical Theory of Evolution Pearson 1894 (Pearson 1894 moments)` | top 5 (relevance) | 2109 | 5 |
| 35 | Estimation | OpenAlex | `Consistent estimation of the order of mixture models of distributions with BIC Keribin 2000 (Keribin 2000 BIC order)` | top 5 (relevance) | 241 | 0 |
| 36 | Structure-K | OpenAlex | `Assessing a mixture model for clustering with the integrated completed likelihood Biernacki 2000 (Biernacki 2000 ICL)` | top 5 (relevance) | 901 | 1 |
| 37 | Estimation | OpenAlex | `Numerical maximum likelihood estimation: An alternative to the EM algorithm MacDonald 2014 (MacDonald 2014 Direct ML)` | top 5 (relevance) | 698 | 5 |
| 38 | Estimation | OpenAlex | `Maximum likelihood estimation via the ECM algorithm A general framework Meng Rubin 1993 (Meng Rubin 1993 ECM)` | top 5 (relevance) | 739 | 4 |
| 39 | Estimation | OpenAlex | `The ECME algorithm a simple extension of EM and ECM with faster monotone convergence Liu Rubin 1994 (Liu Rubin 1994 ECME)` | top 5 (relevance) | 210 | 2 |
| 40 | Estimation | OpenAlex | `Consistent estimation of a mixing distribution Leroux 1992 (Leroux 1992 mixing distribution)` | top 5 (relevance) | 1732 | 3 |
| 41 | Estimation | OpenAlex | `Minimum Hellinger distance estimation for normal models Woodward 1984 (Woodward 1984 MHD)` | top 5 (relevance) | 28 | 2 |
| 42 | Foundations | OpenAlex | `On the Identifiability of Finite Mixtures Yakowitz Spragins 1968 (Yakowitz Spragins 1968 Identifiability)` | top 5 (relevance) | 206 | 3 |
| 43 | Structure-K | OpenAlex | `On bootstrapping the likelihood ratio test statistic for the number of components in a normal mixture McLachlan 1987 (McLachlan 1987 bootstrap LRT)` | top 5 (relevance) | 572 | 4 |
| 44 | Estimation | OpenAlex | `Polynomial-time algorithms for estimating mixtures of Gaussians Belkin Sinha 2010 (Belkin Sinha 2010 moments polynomial)` | top 5 (relevance) | 155 | 5 |
| 45 | Estimation | OpenAlex | `Moment matrices and distance methods for finite mixture models Lindsay 1989 (Lindsay 1989 moment matrices)` | top 5 (relevance) | 258 | 4 |
| 46 | Initialization | OpenAlex | `Initializing partition-optimization algorithms Maitra 2009 (Maitra 2009 initialization)` | top 5 (relevance) | 787 | 5 |
| 47 | Structure-Family | OpenAlex | `Finite mixtures of distributions with different component families (Heterogeneous component families)` | top 5 (relevance) | 87757 | 3 |
| 48 | Structure-Family | OpenAlex | `Mixture models with different component distributions Yu 2012 (Yu 2012 different component distributions)` | top 5 (relevance) | 366901 | 4 |
| 49 | Structure-Family | OpenAlex | `Univariate continuous finite mixtures heterogeneous components survival (Heterogeneous mixtures survival / reliability)` | top 5 (relevance) | 1047 | 4 |
| 50 | Structure-Family | OpenAlex | `Selection of component distributions in finite mixture models (Component distribution family selection)` | top 5 (relevance) | 129397 | 1 |
| 51 | Structure-Family | OpenAlex | `A mixture of gamma and weibull distributions wind speed (Gamma Weibull mixture wind speed)` | top 5 (relevance) | 1322 | 3 |
| 52 | Structure-Family | OpenAlex | `mixture of lognormal and normal distributions (Lognormal Normal mixture)` | top 5 (relevance) | 18897 | 3 |
| 53 | Structure-Family | OpenAlex | `mixR: An R Package for Finite Mixture Modeling for Normal and Non-normal Data (mixR R package Yu 2018)` | top 5 (relevance) | 26 | 3 |
| 54 | Structure-Family | OpenAlex | `mixtools: An R Package for Analyzing Finite Mixture Models Benaglia 2009 (mixtools Benaglia 2009)` | top 5 (relevance) | 711 | 3 |

## 3. Протокол запросов Этапа II (ML-методы обработки структуры одномерных конечных смесей: вычисление K и семейств)

- **Дата проведения:** 2026-10-21
- **Целевая область:** Методы машинного обучения (ML) для решения двух ключевых структурных задач одномерных непрерывных конечных смесей (1D Continuous Finite Mixture Models, FMM):
  1. Вычисление / автоматический подбор количества компонент ($K$);
  2. Вычисление / выбор параметрических семейств распределений компонент (включая разнородные непрерывные смеси: Normal, Weibull, Gamma, Lognormal).
- **Основные базы:** OpenAlex API, CrossRef, arXiv, PMLR / NeurIPS Proceedings, Journal of Machine Learning Research (JMLR), Journal of Statistical Software (JSS).
- **Правило скрининга:** Строго одномерные непрерывные конечные смеси (1D Continuous FMM). Полностью исключены: бесконечные смеси (Dirichlet Process, DP-GMM, CRP), многомерные графические модели (SPN, Bayesian Networks), дискретные/категориальные модели (LCA, poLCA), а также обычные автоэнкодеры с непрерывным латентным пространством (VAE) и условные регрессоры (MDN).

| № | Направление | Источник | Поисковый запрос / путь | Глубина и сортировка | Всего в базе | Новых в каталог |
|---|---|---|---|---|---|---|
| 55 | ML-Structure-K | OpenAlex | `greedy learning finite mixture models components` | top 10 (relevance) | 9874 | 2 (Vlassis 2002, Verbeek 2003) |
| 56 | ML-Structure-K | OpenAlex | `split and merge EM algorithm mixture order` | top 10 (relevance) | 10068 | 1 (Ueda 2000) |
| 57 | ML-Structure-K | OpenAlex | `unsupervised learning finite mixture minimum message length` | top 10 (relevance) | 2619 | 1 (Figueiredo & Jain 2002) |
| 58 | ML-Structure-K | OpenAlex | `sparse Dirichlet prior mixture component pruning` | top 10 (relevance) | 1077 | 1 (Corduneanu & Bishop 2001) |
| 59 | ML-Structure-K | OpenAlex/CrossRef | `variational Bayes finite mixture model selection ELBO` | top 10 (relevance) | 3820 | 1 (Wang & Yang 2026) |
| 60 | ML-Structure-K | OpenAlex | `G-means clustering gaussian mixture order` | top 10 (relevance) | 113271 | 2 (Pelleg 2000, Hamerly 2003) |
| 61 | ML-Structure-K | OpenAlex/CrossRef | `modal EM algorithm Gaussian mixture component merging` | top 10 (relevance) | 412 | 1 (Scrucca 2021) |
| 62 | ML-Structure-K | OpenAlex | `nonparametric maximum likelihood estimation finite mixtures support` | top 10 (relevance) | 15593 | 1 (Böhning 1992 CAMAN) |
| 63 | ML-Structure-K | OpenAlex | `merging mixture components unimodality clustering Hennig` | top 10 (relevance) | 119 | 2 (Hennig 2010, Baudry 2010) |
| 64 | ML-Structure-Family | OpenAlex | `component distribution selection finite mixture models` | top 10 (relevance) | 130189 | 1 (Hosking 1990) |
| 65 | ML-Structure-Family | OpenAlex | `heterogeneous finite mixture model selection genetic algorithm` | top 10 (relevance) | 9444 | 1 (Pernkopf 2005) |
| 66 | ML-Structure-K | CrossRef | `evolutionary split and merge Gaussian mixture learning` | top 10 (relevance) | 315 | 1 (Covões & Hruschka 2011) |
| 67 | ML-Structure-K | CrossRef | `modal distance model selection mixture components` | top 10 (relevance) | 540 | 1 (Ray & Lindsay 2008) |
| 68 | ML-Structure-K | CrossRef | `greedy merge learning Gaussian mixture model` | top 10 (relevance) | 180 | 1 (Li & Li 2009) |

## 4. Протокол запросов Этапа III (ML-модели на статистических фичах для предсказания структуры одномерных конечных смесей: K и семейств)

- **Дата проведения:** 2026-10-21
- **Целевая область:** Обучение supervised ML-моделей (Random Forest, Gradient Boosting, 1D CNN, Deep Sets, MLP) на извлекаемых статистических фичах и дескрипторах формы одномерных данных для прямого предсказания структуры **одномерных непрерывных конечных смесей (1D Continuous FMM)**:
  1. Предсказание конечного числа компонент ($K \in \{1, \dots, K_{max}\}$);
  2. Предсказание и классификация параметрических семейств компонент (Normal, Weibull, Gamma, Lognormal, Pareto, Student-t).
- **Жесткие ограничения предметной области:**
  - Строго **конечные смеси (FMM)**: бесконечные смеси (Dirichlet Process, DP-GMM, CRP) полностью исключены;
  - Строго **одномерные непрерывные данные** ($x \in \mathbb{R}$): многомерные пространства ($p > 1$) и дискретные/категориальные распределения (LCA, Poisson, Binomial) полностью исключены.
- **Целевая архитектура пайплайна:**
  `1D выборка x` $\longrightarrow$ `[Извлечение фичей: L-моменты, квантили, ECDF, ECF, гистограмма, энтропия]` $\longrightarrow$ `[Supervised ML: Random Forest / Boosting / 1D CNN / Deep Sets]` $\longrightarrow$ `[Предсказанные K и семейства]`

| № | Направление | Источник | Поисковый запрос / путь | Глубина и сортировка | Всего в базе | Новых в каталог |
|---|---|---|---|---|---|---|
| 70 | ML-Feature-K | OpenAlex | `meta-learning predicting number of clusters meta-features` | top 10 (relevance) | 248700 | 1 (Pimentel 2020) |
| 71 | ML-Feature-K | OpenAlex | `predicting number of mixture components random forest features` | top 10 (relevance) | 80607 | 1 (Sáez & Corchado 2019) |
| 72 | ML-Feature-K | OpenAlex | `learning to predict number of clusters dataset features` | top 10 (relevance) | 557383 | 1 (Hennig 2006 fpc) |
| 73 | ML-Feature-Family | OpenAlex | `classifying probability distribution neural network empirical data` | top 10 (relevance) | 214932 | 1 (Khoussi 2021 NIST) |
| 74 | ML-Feature-Family | OpenAlex | `identifying probability distribution machine learning moments quantiles` | top 10 (relevance) | 8364 | 1 (Hosking 1990 L-moments) |
| 75 | ML-Feature-K | OpenAlex | `estimating mixture order neural network moments quantiles` | top 10 (relevance) | 2714 | 1 (Carreira-Perpiñán 2000) |
| 76 | ML-Amortized-FMM | OpenAlex | `amortized Bayesian inference finite mixture models` | top 10 (relevance) | 1393 | 1 (Kucharský & Bürkner 2026) |
| 77 | ML-Feature-K | OpenAlex | `deep learning prediction number of components Gaussian mixture` | top 10 (relevance) | 73740 | 1 (Warin 2023) |
| 78 | ML-Feature-Family | OpenAlex | `feature-based distribution selection machine learning` | top 10 (relevance) | 812337 | 1 (Zammit-Mangion 2024) |
| 79 | ML-Feature-K | OpenAlex | `recommending number of clusters meta-learning Pimentel` | top 10 (relevance) | 1658 | 1 (Pimentel 2020) |
| 80 | ML-Feature-Family | CrossRef/arXiv | `quantile and moment neural networks distribution learning Warin` | top 10 (relevance) | 480 | 1 (Warin 2023) |
| 81 | ML-Amortized-FMM | CrossRef/NeurIPS | `permutation invariant deep sets finite mixture parameters Zaheer` | top 10 (relevance) | 6500 | 1 (Zaheer 2017 Deep Sets) |
| 82 | ML-Amortized-FMM | CrossRef | `neural methods amortized inference parameter estimation Zammit-Mangion` | top 10 (relevance) | 1200 | 1 (Zammit-Mangion 2024) |
