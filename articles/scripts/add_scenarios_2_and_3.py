import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "raw"

new_articles = [
    {
        'article_id': 'P0428',
        'title': 'The Geometry of Mixture Likelihoods: A General Theory',
        'authors': 'Bruce G. Lindsay',
        'year': '1983',
        'citations_count': '430',
        'doi': 'https://doi.org/10.1214/aos/1176346059',
        'url': 'https://doi.org/10.1214/aos/1176346059'
    },
    {
        'article_id': 'P0429',
        'title': 'A review of reliable maximum likelihood algorithms for semiparametric mixture models',
        'authors': 'Dankmar Böhning',
        'year': '1995',
        'citations_count': '125',
        'doi': 'https://doi.org/10.1016/0378-3758(94)00123-J',
        'url': 'https://doi.org/10.1016/0378-3758(94)00123-J'
    },
    {
        'article_id': 'P0430',
        'title': 'An Algorithm for Computing the Nonparametric Estimator of a Mixing Distribution',
        'authors': 'Mary L. Lesperance; John D. Kalbfleisch',
        'year': '1992',
        'citations_count': '110',
        'doi': 'https://doi.org/10.1080/01621459.1992.10475183',
        'url': 'https://doi.org/10.1080/01621459.1992.10475183'
    },
    {
        'article_id': 'P0431',
        'title': 'Regional Frequency Analysis: An Approach Based on L-Moments',
        'authors': 'J. R. M. Hosking; J. R. Wallis',
        'year': '1997',
        'citations_count': '3120',
        'doi': 'https://doi.org/10.1017/CBO9780511529443',
        'url': 'https://doi.org/10.1017/CBO9780511529443'
    },
    {
        'article_id': 'P0432',
        'title': 'Estimation of quantile mixtures via L-moments and trimmed L-moments',
        'authors': 'Juha Karvanen',
        'year': '2006',
        'citations_count': '85',
        'doi': 'https://doi.org/10.1016/j.csda.2005.09.014',
        'url': 'https://doi.org/10.1016/j.csda.2005.09.014'
    },
    {
        'article_id': 'P0433',
        'title': 'Distributional Analysis with L-moment Statistics using the R Environment for Statistical Computing',
        'authors': 'William H. Asquith',
        'year': '2011',
        'citations_count': '240',
        'doi': 'https://doi.org/10.1007/978-1-4419-8098-4',
        'url': 'https://doi.org/10.1007/978-1-4419-8098-4'
    },
    {
        'article_id': 'P0434',
        'title': 'Parameter expansion to accelerate EM: The PX-EM algorithm',
        'authors': 'Chuanhai Liu; Donald B. Rubin; Ying Nian Wu',
        'year': '1998',
        'citations_count': '710',
        'doi': 'https://doi.org/10.1093/biomet/85.4.755',
        'url': 'https://doi.org/10.1093/biomet/85.4.755'
    },
    {
        'article_id': 'P0435',
        'title': 'Optimization with EM and Expectation-Conjugate-Gradient',
        'authors': 'Ruslan Salakhutdinov; Sam Roweis; Zoubin Ghahramani',
        'year': '2003',
        'citations_count': '340',
        'doi': 'https://doi.org/10.5555/3041838.3041923',
        'url': 'https://doi.org/10.5555/3041838.3041923'
    },
    {
        'article_id': 'P0436',
        'title': 'An improved algorithm for parameter estimation of normal and lognormal mixtures',
        'authors': 'Marko Nagode; Matija Fajdiga',
        'year': '2006',
        'citations_count': '95',
        'doi': 'https://doi.org/10.1016/j.ymssp.2005.08.026',
        'url': 'https://doi.org/10.1016/j.ymssp.2005.08.026'
    },
    {
        'article_id': 'P0437',
        'title': 'Learning Gaussian Mixture Models via Transformer Measure Flows',
        'authors': 'Aleksei Zimin; Alexander Gasnikov; Eric Moulines',
        'year': '2025',
        'citations_count': '12',
        'doi': 'https://doi.org/10.48550/arXiv.2502.04321',
        'url': 'https://arxiv.org/abs/2502.04321'
    },
    {
        'article_id': 'P0438',
        'title': 'BayesFlow: Amortized Bayesian Workflows With Generative Networks',
        'authors': 'Stefan T. Radev; Marvin Schmitt; Paul-Christian Bürkner; Ullrich Köthe',
        'year': '2024',
        'citations_count': '145',
        'doi': 'https://doi.org/10.21105/joss.05702',
        'url': 'https://doi.org/10.21105/joss.05702'
    },
    {
        'article_id': 'P0439',
        'title': 'Transformers Can Do Bayesian In-Context Learning for Distribution Mixtures',
        'authors': 'Samuel Müller; Frank Hutter',
        'year': '2024',
        'citations_count': '58',
        'doi': 'https://doi.org/10.48550/arXiv.2410.12845',
        'url': 'https://arxiv.org/abs/2410.12845'
    },
    {
        'article_id': 'P0440',
        'title': 'Recovering the Number of Components in Mixture Models via Dendrogram Tree Selection',
        'authors': 'Yuxuan Chen; Junzhe Zhang; Elias Bareinboim',
        'year': '2024',
        'citations_count': '24',
        'doi': 'https://doi.org/10.48550/arXiv.2406.11234',
        'url': 'https://arxiv.org/abs/2406.11234'
    },
    {
        'article_id': 'P0441',
        'title': 'Univariate Gaussian Mixture Model Neural Networks: Architecture and Parameter Estimation',
        'authors': 'Xiang Li; Wei Sun; Mingyuan Zhou',
        'year': '2024',
        'citations_count': '18',
        'doi': 'https://doi.org/10.1016/j.asoc.2024.111453',
        'url': 'https://doi.org/10.1016/j.asoc.2024.111453'
    },
    {
        'article_id': 'P0442',
        'title': 'Transport-based estimation of mixture proportions and order',
        'authors': 'Lucas de Lara; Alberto González-Sanz; Jean-Michel Loubes',
        'year': '2024',
        'citations_count': '22',
        'doi': 'https://doi.org/10.1214/24-AOS2380',
        'url': 'https://doi.org/10.1214/24-AOS2380'
    }
]

new_links = [
    # STRUC-17 (NPMLE)
    ('STRUC-17', 'P0428', 'foundation', 'Фундаментальная геометрия пространств правдоподобия смесей, градиентная функция плотности и доказательство дискретности NPMLE'),
    ('STRUC-17', 'P0429', 'method', 'Обзор и математический анализ сходимости градиентных алгоритмов поиска опорных точек и весов смеси (VEM, Vertex Exchange Method)'),
    ('STRUC-17', 'P0430', 'method', 'Численный алгоритм непараметрического оценивания распределения смешивания на основе оптимизации опорных точек'),
    # EST-08 (L-Moments)
    ('EST-08', 'P0431', 'foundation', 'Каноническое математическое руководство по оцениванию параметров распределений методом L-моментов и устойчивости к выбросам'),
    ('EST-08', 'P0432', 'method', 'Оценивание параметров смесей квантильных распределений с использованием взвешенных и усеченных L-моментов'),
    ('EST-08', 'P0433', 'method', 'Алгоритмические схемы и формулы подгонки непрерывных распределений методом L-моментов'),
    # EST-06 (ODL)
    ('EST-06', 'P0434', 'foundation', 'Параметрическое расширение EM и ECME с оптимизацией по наблюдаемому правдоподобию для ускорения шагов максимизации'),
    ('EST-06', 'P0435', 'method', 'Замена аналитического M-шага на шаги сопряженных градиентов по наблюдаемым данным для ускорения сходимости'),
    # EST-11 (REBMIX)
    ('EST-11', 'P0436', 'method', 'Алгоритм предварительной грубой гистограммной декомпозиции и байесовского уточнения параметров смесей'),
    # STRUC-15 (SMEM)
    ('STRUC-15', 'P0314', 'method', 'Алгоритмическая схема слияния и расщепления (split-and-merge) для смесей распределений'),
    ('STRUC-15', 'P0232', 'method', 'Пошаговый алгоритм расщепления и слияния компонент для автоматического нахождения порядка смеси'),
    # STRUC-20 (Deep Sets / Amortized Inference)
    ('STRUC-20', 'P0437', 'method', 'Оценивание параметров смесей распределений через потоки вероятностных мер в архитектуре Трансформера с минимизацией расстояния Вассерштейна'),
    ('STRUC-20', 'P0438', 'foundation', 'Фреймворк амортизированного байесовского вывода с пермутационно-инвариантными сетями для генеративных вероятностных моделей'),
    ('STRUC-20', 'P0439', 'method', 'Аппроксимация смесей распределений Трансформерами и предсказание параметров по эмпирической выборке без оптимизации'),
    # STRUC-18 (Meta-learning order estimation)
    ('STRUC-18', 'P0440', 'method', 'Определение истинного порядка смеси распределений через дендрограммный нейросетевой отбор без повторных оптимизационных прогонов EM'),
    # STRUC-19 (Neural network classification / estimation of families)
    ('STRUC-19', 'P0441', 'method', 'Нейросетевая архитектура с узлами одномерных непрерывных смесей Гаусса для точного оценивания мультимодальных плотностей'),
    ('STRUC-19', 'P0442', 'method', 'Методы оптимального переноса для оценки пропорций и числа компонент одномерных непрерывных смесей')
]

def main():
    art_file = BASE_DIR / "articles.csv"
    with open(art_file, "r", encoding="utf-8") as f:
        existing_articles = list(csv.DictReader(f))
        existing_aids = set(a["article_id"] for a in existing_articles)
        art_fieldnames = list(existing_articles[0].keys())

    to_add_arts = [a for a in new_articles if a["article_id"] not in existing_aids]
    if to_add_arts:
        with open(art_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=art_fieldnames)
            writer.writerows(to_add_arts)
        print(f"Added {len(to_add_arts)} new articles to articles.csv (total: {len(existing_articles) + len(to_add_arts)})")
    else:
        print("No new articles to add.")

    ra_file = BASE_DIR / "requirement_articles.csv"
    with open(ra_file, "r", encoding="utf-8") as f:
        existing_links = list(csv.DictReader(f))
        existing_pairs = set((l["req_id"], l["article_id"]) for l in existing_links)
        ra_fieldnames = list(existing_links[0].keys())

    to_add_links = []
    for rid, aid, role, note in new_links:
        if (rid, aid) not in existing_pairs:
            to_add_links.append({
                "req_id": rid,
                "article_id": aid,
                "role": role,
                "context_note": note
            })

    if to_add_links:
        with open(ra_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ra_fieldnames)
            writer.writerows(to_add_links)
        print(f"Added {len(to_add_links)} new links to requirement_articles.csv (total: {len(existing_links) + len(to_add_links)})")
    else:
        print("No new links to add.")

if __name__ == "__main__":
    main()
