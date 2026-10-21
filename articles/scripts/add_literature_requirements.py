import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "raw"

new_requirements = [
    {
        'req_id': 'EST-17',
        'type': 'estimation',
        'name': 'Взвешенные наблюдения и веса выборки',
        'description': 'Поддержка весов на уровне отдельных наблюдений (частотные веса, вероятностные веса выборки или веса важности) в процедурах оценивания. В шагах алгоритма веса наблюдений мультипликативно учитываются при расчете апостериорных вероятностей принадлежности и взвешенных достаточных статистик на шаге максимизации параметров компонент.',
        'discovered_in': 'Gaussian Mixture Estimation from Weighted Samples (P0136), scikit-learn, FlexMix',
        'priority': 'should'
    },
    {
        'req_id': 'EST-18',
        'type': 'estimation',
        'name': 'Оценивание по цензурированным и усеченным данным',
        'description': 'Адаптация алгоритмов оценивания параметров для непрерывных данных с правосторонним, левосторонним или интервальным цензурированием, а также левосторонним или двусторонним усечением носителя. На шаге оценивания функция правдоподобия и апостериорные веса корректируются с учетом интегральных вероятностей попадания за порог цензурирования или усечения области определения.',
        'discovered_in': 'A framework for ML estimation with optional truncation or censoring (P0339), mixR',
        'priority': 'could'
    },
    {
        'req_id': 'EST-19',
        'type': 'estimation',
        'name': 'Ускорение сходимости EM-алгоритма (Aitken, SQUAREM)',
        'description': 'Применение методов экстраполяции шагов и квазиньютоновских ускорений к последовательности оценок параметров между итерациями алгоритма. Позволяет преодолеть медленную линейную сходимость классического итерационного процесса в окрестности плато правдоподобия или сильно перекрывающихся компонент за счет квадратичной экстраполяции приращений вектора параметров.',
        'discovered_in': 'Acceleration of the EM algorithm (P0125), Quasi-Newton acceleration (P0036), mclust',
        'priority': 'could'
    },
    {
        'req_id': 'EST-20',
        'type': 'estimation',
        'name': 'Рекурсивный потоковый EM-алгоритм',
        'description': 'Потоковое и последовательное оценивание параметров смеси для бесконечных потоков данных или пакетов наблюдений без необходимости хранения всей выборки в оперативной памяти. Достаточные статистики компонент обновляются рекурсивно по схеме стохастической аппроксимации с затухающим шагом обучения при поступлении новых порций наблюдений.',
        'discovered_in': 'Recursive unsupervised learning of finite mixture models (P0030, P0208), bnpy',
        'priority': 'could'
    },
    {
        'req_id': 'EST-21',
        'type': 'estimation',
        'name': 'Оценивание методом минимального расстояния Хеллингера',
        'description': 'Альтернативный метод оценивания параметров смеси посредством минимизации интегрального расстояния Хеллингера или степенных расхождений между эмпирической непараметрической оценкой плотности и теоретической моделью смеси. Обеспечивает устойчивость к грубым выбросам и высокой степени засорения выборки без потери асимптотической эффективности.',
        'discovered_in': 'Minimum Hellinger Distance Estimation for Finite Mixture Models (P0054, P0076, P0171)',
        'priority': 'could'
    },
    {
        'req_id': 'STRUC-21',
        'type': 'structure',
        'name': 'Равенство и линейные ограничения параметров компонент',
        'description': 'Наложение межкомпонентных равенств и линейных связей на параметры масштаба, формы или сдвига между различными компонентами смеси (например, предположение об общей дисперсии всех компонент или общих коэффициентах формы). Существенно сокращает размерность пространства оцениваемых параметров и защищает от переобучения на выборках малого объема.',
        'discovered_in': 'FlexMix with varying and constant parameters (P0027), Parsimonious modeling (P0096), mclust',
        'priority': 'should'
    },
    {
        'req_id': 'STRUC-22',
        'type': 'structure',
        'name': 'Асимметричные и тяжелохвостые семейства (Skew-Normal, Student-t)',
        'description': 'Поддержка параметрических распределений с дополнительными степенями свободы для формы хвостов и асимметрии, таких как распределение Стьюдента и скошенное нормальное распределение. Позволяет моделировать кластеры с выраженными длинными хвостами и внутренней асимметрией одной компонентой вместо искусственного раздувания числа компонент смеси.',
        'discovered_in': 'Finite mixture modelling using skew normal and skew-t (P0034, P0035, P0140, P0323), teigen, sn',
        'priority': 'could'
    },
    {
        'req_id': 'STRUC-23',
        'type': 'structure',
        'name': 'Вариационный байесовский вывод (VBEM)',
        'description': 'Аналитическая байесовская аппроксимация совместного апостериорного распределения параметров смеси и латентных переменных с помощью вариационной оптимизации нижней границы обоснованности данных. Обеспечивает автоматическое зануление весов избыточных компонент через регуляризацию априорным распределением Дирихле и устраняет необходимость перебора моделей по сетке.',
        'discovered_in': 'Variational Bayesian Model Selection (P0020, P0028, P0417), scikit-learn, bnpy',
        'priority': 'could'
    },
    {
        'req_id': 'DIAG-04',
        'type': 'diagnostics',
        'name': 'Оценка отделимости и перекрытия компонент',
        'description': 'Количественные показатели четкости разделения кластеров и меры межкомпонентного наложения, включая нормализованный критерий энтропии классификации, среднюю апостериорную вероятность отнесения и матрицу парных дистанций между плотностями компонент. Позволяет выявлять скрытую избыточность числа компонент и ненадежность классификационных решений.',
        'discovered_in': 'Variants of EM Algorithm and entropy measures (P0013, P0015, P0113), fpc',
        'priority': 'could'
    }
]

new_req_articles = [
    # EST-17
    ('EST-17', 'P0136', 'foundation', 'Теоретическое обоснование и вывод уравнений EM-шага для смесей Гауссиан по взвешенным выборкам'),
    ('EST-17', 'P0258', 'method', 'Взвешенные статистические тесты однородности для проверки числа компонент смеси'),
    ('EST-17', 'P0319', 'method', 'Максимизация взвешенного правдоподобия в EM-алгоритме для автоматического выбора модели'),
    # EST-18
    ('EST-18', 'P0268', 'method', 'Методология выборочного оценивания при наличии цензурированных наблюдений'),
    ('EST-18', 'P0339', 'foundation', 'Аналитическая структура шагов максимального правдоподобия для параметров смесей при цензурировании и усечении'),
    ('EST-18', 'P0363', 'method', 'Регрессионные модели смесей для цензурированных данных на основе асимметричных распределений'),
    # EST-19
    ('EST-19', 'P0036', 'foundation', 'Квазиньютоновское ускорение итерационных оптимизационных алгоритмов высокой размерности'),
    ('EST-19', 'P0125', 'method', 'Методы и алгоритмические схемы ускорения сходимости EM-алгоритма в моделях смесей'),
    ('EST-19', 'P0228', 'method', 'Гибридный алгоритм EM и Гаусса-Ньютона для ускорения поиска оценок максимального правдоподобия'),
    # EST-20
    ('EST-20', 'P0030', 'foundation', 'Рекурсивное обучение параметров конечных смесей в потоковом режиме без учителя'),
    ('EST-20', 'P0208', 'method', 'Доказательство сходимости версии стохастической аппроксимации EM-алгоритма'),
    ('EST-20', 'P0237', 'method', 'Асимптотическая состоятельность рекурсивных оценок параметров смеси'),
    ('EST-20', 'P0286', 'method', 'Геометрический фреймворк градиентного потока для рекурсивного оценивания смесей'),
    # EST-21
    ('EST-21', 'P0054', 'foundation', 'Оценивание параметров конечных смесей методом минимизации расстояния Хеллингера'),
    ('EST-21', 'P0076', 'method', 'Метод минимального расстояния Хеллингера для робастных моделей регрессии смесей'),
    ('EST-21', 'P0100', 'method', 'Профильное расстояние Хеллингера для полупараметрических моделей смесей'),
    ('EST-21', 'P0171', 'benchmark', 'Сравнительный анализ устойчивости метода минимального расстояния L2 и EM-алгоритма'),
    # STRUC-21
    ('STRUC-21', 'P0027', 'foundation', 'Фреймворк FlexMix: модели смесей с константными и варьирующимися параметрами между компонентами'),
    ('STRUC-21', 'P0096', 'method', 'Экономное моделирование ковариационных матриц и выбор порядка многомерных смесей'),
    ('STRUC-21', 'P0217', 'method', 'Экономные параметрические ограничения в смесях нормальных распределений с загрязнениями'),
    # STRUC-22
    ('STRUC-22', 'P0034', 'foundation', 'Байесовский вывод для одномерных и многомерных смесей скошенных нормальных и Стьюдента распределений'),
    ('STRUC-22', 'P0035', 'method', 'Моделирование смесей с использованием скошенного нормального распределения'),
    ('STRUC-22', 'P0140', 'method', 'EM-алгоритм для оценивания обобщенного скошенного распределения Стьюдента в робастных смесях'),
    ('STRUC-22', 'P0323', 'foundation', 'Оценивание максимального правдоподобия для многомерного распределения Стьюдента через EM-алгоритм'),
    # STRUC-23
    ('STRUC-23', 'P0020', 'foundation', 'Байесовский анализ смесей с неизвестным числом компонент'),
    ('STRUC-23', 'P0028', 'foundation', 'Вариационный байесовский отбор моделей и регуляризация для смесей распределений'),
    ('STRUC-23', 'P0216', 'method', 'Вариационные аппроксимации в байесовском выборе моделей смесей'),
    ('STRUC-23', 'P0417', 'method', 'Оценивание числа компонент конечных смесей с помощью вариационной аппроксимации'),
    # DIAG-04
    ('DIAG-04', 'P0013', 'method', 'Анализ вариантов EM-алгоритма, энтропийных мер и устойчивости классификации'),
    ('DIAG-04', 'P0015', 'foundation', 'Доверительный отбор порядка смесей и критерии надежности разделения компонент'),
    ('DIAG-04', 'P0113', 'method', 'Быстрые аппроксимации дивергенции Джеффриса между компонентами для оценки наложения')
]

eval_data = {
    'EST-17': {
        'pysatl-mpest': ('no', 'Веса наблюдений и частотные веса не поддерживаются в текущей версии пайплайна оценивания', ''),
        'scikit-learn': ('yes', 'Аргумент sample_weight поддерживается в методе fit для GaussianMixture и BayesianGaussianMixture', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('yes', 'Параметр sample_weight поддерживается во всех моделях GeneralMixtureModel', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Взвешивание наблюдений не предусмотрено сигнатурой em()', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('yes', 'Параметр sample_weight поддерживается в методе fit', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Веса наблюдений не поддерживаются', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Веса наблюдений не поддерживаются', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Веса наблюдений не поддерживаются в модуле подгонки', 'https://github.com/erdogant/distfit'),
        'mclust': ('yes', 'Параметр weights поддерживается в функции densityMclust и алгоритмах кластеризации', 'https://github.com/cran/mclust'),
        'mixtools': ('yes', 'Параметр w поддерживается во многих процедурах подгонки смесей', 'https://github.com/cran/mixtools'),
        'flexmix': ('yes', 'Аргумент weights встроен в формулу спецификации модели flexmix', 'https://github.com/cran/flexmix'),
        'mixR': ('yes', 'Параметр weights в функции mixfit для частотного взвешивания', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('yes', 'Параметр Weights в функции REBMIX для взвешенных выборок', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('yes', 'Параметр weight в процедуре mixmodCluster', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('yes', 'Параметр sample_weight в GMM_EM', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('yes', 'Входные данные в виде сгруппированных частотных весов и интервалов', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Веса наблюдений не поддерживаются', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('no', 'Веса наблюдений не поддерживаются', 'https://github.com/cran/teigen'),
        'fpc': ('partial', 'Ограниченная поддержка весов через обертки над mclust', 'https://github.com/cran/fpc'),
        'sn': ('yes', 'Параметр weights в функциях selm и dmsn', 'https://github.com/cran/sn'),
        'brms': ('yes', 'Поддержка весов наблюдений через формульный синтаксис weights()', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Веса наблюдений не поддерживаются', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('yes', 'Функция fit(MixtureModel, ...) поддерживает аргумент Weights', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Веса наблюдений не поддерживаются в mlpack::gmm', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Класс gmm_diag не поддерживает веса точек данных', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('yes', 'Поддержка весов наблюдений в контейнерах DataObj', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('yes', 'Поддержка весов и частот наблюдений через аргумент weights в mixalg', 'https://github.com/cran/CAMAN'),
    },
    'EST-18': {
        'pysatl-mpest': ('no', 'Оценивание по цензурированным и усеченным наблюдениям отсутствует; требуется полная выборка', ''),
        'scikit-learn': ('no', 'Цензурированные и усеченные выборки не поддерживаются', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Цензурирование не поддерживается', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Цензурирование не поддерживается', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Цензурированные выборки не поддерживаются', 'https://github.com/erdogant/distfit'),
        'mclust': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/cran/mclust'),
        'mixtools': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/cran/mixtools'),
        'flexmix': ('partial', 'Поддержка моделей выживаемости и цензурирования через драйвер FLXMRglm', 'https://github.com/cran/flexmix'),
        'mixR': ('yes', 'Явная поддержка левостороннего, правостороннего и интервального цензурирования через параметры rcensored и lcensored', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Цензурирование не поддерживается', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('no', 'Цензурированные непрерывные наблюдения не поддерживаются напрямую', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/cran/fpc'),
        'sn': ('no', 'Цензурирование не поддерживается', 'https://github.com/cran/sn'),
        'brms': ('yes', 'Полная поддержка цензурирования cens() и усечения trunc() в смесях через Stan', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Цензурирование не поддерживается', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('partial', 'Обертка Truncated поддерживается для одиночных распределений, но без специализированного EM для смеси', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Цензурирование не поддерживается', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('no', 'Цензурированные данные не поддерживаются', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Цензурированные наблюдения не поддерживаются', 'https://github.com/cran/CAMAN'),
    },
    'EST-19': {
        'pysatl-mpest': ('no', 'Экстраполяция шагов и алгоритмы ускорения сходимости (Aitken, SQUAREM) не реализованы', ''),
        'scikit-learn': ('no', 'Используются стандартные EM-итерации без процедур экстраполяции сходимости', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('no', 'Ускорения типа SQUAREM или Aitken не реализованы', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Ускорение сходимости не реализовано', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('no', 'Ускорение EM-алгоритма не реализовано', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Ускорения сходимости нет', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Ускорение EM-алгоритма отсутствует', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Ускорение сходимости не применимо', 'https://github.com/erdogant/distfit'),
        'mclust': ('partial', 'Критерий остановки на основе ускорения Эйткена (Aitken acceleration)', 'https://github.com/cran/mclust'),
        'mixtools': ('no', 'Ускорения сходимости SQUAREM не встроены', 'https://github.com/cran/mixtools'),
        'flexmix': ('no', 'Используется классический цикл EM без экстраполяции', 'https://github.com/cran/flexmix'),
        'mixR': ('no', 'Ускорение сходимости не реализовано', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Ускорение EM не применимо к алгоритму REB', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Ускорение EM-алгоритма отсутствует', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Ускорения EM нет', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('partial', 'Использует метод квази-Ньютона на наблюдаемом правдоподобии вместо чистого EM', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Экстраполяция сходимости не реализована', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('partial', 'Ускорение Эйткена для оценки асимптотического предела правдоподобия и критерия сходимости', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Ускорение сходимости не реализовано', 'https://github.com/cran/fpc'),
        'sn': ('no', 'Ускорение сходимости отсутствует', 'https://github.com/cran/sn'),
        'brms': ('no', 'Оценивание методом MCMC (NUTS), а не ускоренным EM', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Ускорение сходимости отсутствует', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('no', 'Стандартный EM без ускорения', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Ускорение сходимости не реализовано', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Ускорение сходимости не реализовано', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('partial', 'Ускоренные вариационные аппроксимации и динамическое слияние', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('partial', 'Алгоритмы VEM и градиентного ускорения сходимости для непараметрических смесей', 'https://github.com/cran/CAMAN'),
    },
    'EST-20': {
        'pysatl-mpest': ('no', 'Потоковый и рекурсивный онлайн EM-алгоритм не реализован; требуется полная загрузка данных в память', ''),
        'scikit-learn': ('no', 'Метод partial_fit не реализован для GaussianMixture', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('partial', 'Поддерживается пакетное обучение на генераторах данных через fit(batches=True)', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Потоковое оценивание отсутствует', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('no', 'Потоковый режим не поддерживается', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Потоковый режим не реализован', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Потоковый режим не поддерживается', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Потоковый режим отсутствует', 'https://github.com/erdogant/distfit'),
        'mclust': ('no', 'Потоковый онлайн EM-алгоритм не реализован', 'https://github.com/cran/mclust'),
        'mixtools': ('no', 'Потоковый онлайн EM не реализован', 'https://github.com/cran/mixtools'),
        'flexmix': ('no', 'Потоковый режим не поддерживается', 'https://github.com/cran/flexmix'),
        'mixR': ('no', 'Потоковый онлайн EM не поддерживается', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Потоковый режим не реализован', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Потоковый онлайн EM не поддерживается', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Потоковый режим не реализован', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('no', 'Потоковый режим не поддерживается', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Потоковый режим отсутствует', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('no', 'Потоковый режим отсутствует', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Потоковый режим отсутствует', 'https://github.com/cran/fpc'),
        'sn': ('no', 'Потоковый режим не поддерживается', 'https://github.com/cran/sn'),
        'brms': ('no', 'Потоковый режим не поддерживается', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Потоковый режим отсутствует', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('no', 'Потоковый режим не реализован', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Потоковый онлайн EM не реализован', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Потоковый режим не поддерживается', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('yes', 'Специализированная архитектура для потокового стохастического и мемоизированного онлайн EM-обучения на больших данных', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Потоковый режим не поддерживается', 'https://github.com/cran/CAMAN'),
    },
    'EST-21': {
        'pysatl-mpest': ('no', 'Оценивание методом минимального расстояния Хеллингера не поддерживается', ''),
        'scikit-learn': ('no', 'Оценивание методом расстояния Хеллингера не поддерживается', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('no', 'Метод минимального расстояния Хеллингера отсутствует', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Оценивание по расстоянию Хеллингера не поддерживается', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('no', 'Минимальное расстояние Хеллингера не поддерживается', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Оценивание по расстоянию Хеллингера не реализовано', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Оценивание методом расстояния Хеллингера отсутствует', 'https://github.com/erdogant/distfit'),
        'mclust': ('no', 'Оценивание по расстоянию Хеллингера не поддерживается', 'https://github.com/cran/mclust'),
        'mixtools': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/cran/mixtools'),
        'flexmix': ('no', 'Оценивание методом Хеллингера не реализовано', 'https://github.com/cran/flexmix'),
        'mixR': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Оценивание по расстоянию Хеллингера не поддерживается', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Оценивание по расстоянию Хеллингера не поддерживается', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('partial', 'Поддерживает метод взвешенных наименьших квадратов и минимум хи-квадрат как альтернативу MLE', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/cran/fpc'),
        'sn': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/cran/sn'),
        'brms': ('no', 'Байесовское апостериорное сэмплирование взамен критериев минимального расстояния', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('no', 'Оценивание по расстоянию Хеллингера не поддерживается', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Оценивание по расстоянию Хеллингера отсутствует', 'https://github.com/cran/CAMAN'),
    },
    'STRUC-21': {
        'pysatl-mpest': ('no', 'Межкомпонентные равенства и линейные ограничения параметров компонент не поддерживаются', ''),
        'scikit-learn': ('partial', 'Режим covariance_type="tied" фиксирует общую ковариационную матрицу для всех компонент', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('partial', 'Поддерживается связывание и разделение параметров через граф распределений', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Параметры компонент оцениваются полностью независимо', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('yes', 'Поддерживаются структурные ограничения параметров и инвариантность между скрытыми классами', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Межкомпонентные ограничения параметров не поддерживаются', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Межкомпонентные ограничения отсутствуют', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Ограничения между компонентами не поддерживаются', 'https://github.com/erdogant/distfit'),
        'mclust': ('yes', '14 экономных параметризаций ковариаций с ограничениями на равенство объема, формы и ориентации', 'https://github.com/cran/mclust'),
        'mixtools': ('partial', 'Опция arbvar=FALSE задает равенство дисперсий компонент в нормальных смесях', 'https://github.com/cran/mixtools'),
        'flexmix': ('yes', 'Полная поддержка равенства и фиксации параметров через FLXcontrol и синтаксис моделей', 'https://github.com/cran/flexmix'),
        'mixR': ('partial', 'Опция equal.variance=TRUE для фиксации равных дисперсий нормальных компонент', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Ограничения между компонентами не поддерживаются', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('yes', 'Поддержка четырнадцати экономных моделей ковариационных матриц с ограничениями равенства', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Ограничения равенства параметров отсутствуют', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('yes', 'Параметр constr позволяет накладывать равенства и константные ограничения на параметры', 'https://github.com/cran/mixdist'),
        'EMCluster': ('yes', 'Поддерживает ограничения на общую дисперсию и форму ковариаций', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('yes', 'Поддерживает 14 экономных параметризаций масштабных матриц распределения Стьюдента', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Собственные ограничения параметров не накладываются', 'https://github.com/cran/fpc'),
        'sn': ('partial', 'Возможность фиксации отдельных параметров асимметрии', 'https://github.com/cran/sn'),
        'brms': ('yes', 'Нелинейный синтаксис формул позволяет задавать произвольные ограничения равенства параметров компонент', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Межкомпонентные ограничения отсутствуют', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('no', 'Параметры компонент оцениваются раздельно', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Межкомпонентные ограничения отсутствуют', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Ограничения между компонентами не поддерживаются', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('no', 'Межкомпонентные ограничения параметров не поддерживаются', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Ограничения параметров не поддерживаются', 'https://github.com/cran/CAMAN'),
    },
    'STRUC-22': {
        'pysatl-mpest': ('no', 'Распределения Стьюдента и скошенные нормальные распределения отсутствуют в библиотеке', ''),
        'scikit-learn': ('no', 'Поддерживается только нормальное распределение Гаусса', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('partial', 'Одномерное распределение Стьюдента (StudentT) поддерживается в качестве компоненты', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Только базовые нормальные, экспоненциальные и логнормальные компоненты', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('no', 'Ограничен категориальными и нормальными откликами', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('yes', 'Специализированная библиотека для смесей многомерных распределений Стьюдента', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Только смеси Гауссиан', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('partial', 'Поддерживает распределение Стьюдента для одиночных распределений, но не в смесях', 'https://github.com/erdogant/distfit'),
        'mclust': ('no', 'Только смеси нормальных распределений', 'https://github.com/cran/mclust'),
        'mixtools': ('no', 'Только стандартные экспоненциальные, пуассоновские и нормальные семейства', 'https://github.com/cran/mixtools'),
        'flexmix': ('partial', 'Поддержка обобщенных линейных моделей компонент через семейство FLXMRglm', 'https://github.com/cran/flexmix'),
        'mixR': ('partial', 'Поддерживает Вейбулл, гамма и логнормальные смеси, но не скошенные распределения Стьюдента', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Только классические непрерывные и дискретные семейства', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Только нормальные и мультиномиальные смеси', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Только гауссовы смеси', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('no', 'Стандартные семейства (нормальное, гамма, экспоненциальное, логнормальное)', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Только многомерные нормальные смеси', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('yes', 'Специализированная библиотека для смесей многомерных распределений Стьюдента', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Только гауссовы смеси', 'https://github.com/cran/fpc'),
        'sn': ('yes', 'Каноническая реализация скошенных нормальных и скошенных распределений Стьюдента', 'https://github.com/cran/sn'),
        'brms': ('yes', 'Прямая поддержка семейств student_t и skew_normal в смесях', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Только смеси Гауссиан', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('partial', 'Поддерживает распределение Стьюдента в структуре MixtureModel, но без скошенных модификаций', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Только гауссовы смеси', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Только гауссовы смеси', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('partial', 'Поддержка распределений Лапласа и Гаусса', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Только экспоненциальные и нормальные компоненты', 'https://github.com/cran/CAMAN'),
    },
    'STRUC-23': {
        'pysatl-mpest': ('no', 'Вариационный байесовский вывод (VBEM) не реализован', ''),
        'scikit-learn': ('yes', 'Класс BayesianGaussianMixture реализует вариационный байесовский вывод с априорным процессом Дирихле', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('no', 'Вариационный вывод не реализован; доступен только классический EM', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Вариационный вывод отсутствует', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('no', 'Вариационный байесовский вывод не поддерживается', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('yes', 'Реализован вариационный класс VariationalStudentMixture', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Вариационный вывод отсутствует', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Вариационный вывод отсутствует', 'https://github.com/erdogant/distfit'),
        'mclust': ('no', 'Вариационный вывод не реализован; используется байесовская регуляризация через априорные сопряженные распределения', 'https://github.com/cran/mclust'),
        'mixtools': ('no', 'Вариационный байесовский вывод не поддерживается', 'https://github.com/cran/mixtools'),
        'flexmix': ('no', 'Вариационный вывод отсутствует', 'https://github.com/cran/flexmix'),
        'mixR': ('no', 'Вариационный вывод не поддерживается', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Вариационный вывод отсутствует', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Вариационный вывод не реализован', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Вариационный вывод отсутствует', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('no', 'Вариационный вывод отсутствует', 'https://github.com/cran/mixdist'),
        'EMCluster': ('no', 'Вариационный вывод отсутствует', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('no', 'Вариационный вывод отсутствует', 'https://github.com/cran/teigen'),
        'fpc': ('no', 'Вариационный вывод отсутствует', 'https://github.com/cran/fpc'),
        'sn': ('no', 'Вариационный вывод не реализован', 'https://github.com/cran/sn'),
        'brms': ('partial', 'Поддержка алгоритма вариационного вывода Stan (algorithm="meanfield")', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Вариационный вывод отсутствует', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('no', 'Вариационный вывод отсутствует', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Вариационный вывод отсутствует', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Вариационный вывод отсутствует', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('yes', 'Масштабируемый вариационный байесовский вывод (VBEM) с априорными процессами Дирихле', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Вариационный вывод отсутствует', 'https://github.com/cran/CAMAN'),
    },
    'DIAG-04': {
        'pysatl-mpest': ('no', 'Метрики энтропии разделения и оценки матриц попарного наложения компонент не вычисляются', ''),
        'scikit-learn': ('no', 'Метрики перекрытия и энтропии разделения компонент не рассчитываются', 'https://github.com/scikit-learn/scikit-learn'),
        'pomegranate': ('no', 'Диагностика перекрытия компонент не встроена', 'https://github.com/jmschrei/pomegranate'),
        'mixem': ('no', 'Анализ перекрытия компонент не поддерживается', 'https://github.com/sseemayer/mixem'),
        'stepmix': ('partial', 'Расчет энтропии классификации и относительной энтропии неопределенности', 'https://github.com/Labo-Lacourse/stepmix'),
        'student-mixture': ('no', 'Метрики перекрытия не вычисляются', 'https://github.com/omritomer/student-mixture'),
        'kasakh-gmm': ('no', 'Диагностика отделимости компонент отсутствует', 'https://github.com/kasakh/Mixture-Models'),
        'distfit': ('no', 'Метрики отделимости не рассчитываются', 'https://github.com/erdogant/distfit'),
        'mclust': ('partial', 'Расчет неопределенности классификации (uncertainty) и энтропии отнесения к компонентам', 'https://github.com/cran/mclust'),
        'mixtools': ('partial', 'Функции расчета энтропии апостериорных вероятностей', 'https://github.com/cran/mixtools'),
        'flexmix': ('partial', 'Расчет энтропии и апостериорных мер определенности отнесения', 'https://github.com/cran/flexmix'),
        'mixR': ('no', 'Оценка перекрытия компонент не поддерживается', 'https://github.com/GaryBAYLOR/mixR'),
        'rebmix': ('no', 'Диагностика перекрытия отсутствует', 'https://github.com/cran/rebmix'),
        'Rmixmod': ('no', 'Меры отделимости компонент не рассчитываются', 'https://github.com/mixmod/mixmod'),
        'ClusterR': ('no', 'Меры перекрытия компонент не поддерживаются', 'https://github.com/mlampros/ClusterR'),
        'mixdist': ('no', 'Диагностика перекрытия отсутствует', 'https://github.com/cran/mixdist'),
        'EMCluster': ('partial', 'Функции расчета вероятностей ложной классификации и наложения кластеров', 'https://github.com/snoweye/EMCluster'),
        'teigen': ('partial', 'Метрики неопределенности и энтропии отнесения наблюдений', 'https://github.com/cran/teigen'),
        'fpc': ('yes', 'Функции overlap.exact и overlap.fpc для строгого расчета матрицы взаимного перекрытия компонент', 'https://github.com/cran/fpc'),
        'sn': ('no', 'Диагностика перекрытия компонент не поддерживается', 'https://github.com/cran/sn'),
        'brms': ('no', 'Метрики отделимости не рассчитываются автоматически', 'https://github.com/paul-buerkner/brms'),
        'GaussianMixtures.jl': ('no', 'Диагностика перекрытия не реализована', 'https://github.com/davidavdav/GaussianMixtures.jl'),
        'Distributions.jl': ('no', 'Метрики отделимости компонент не предусмотрены', 'https://github.com/JuliaStats/Distributions.jl'),
        'mlpack': ('no', 'Диагностика отделимости не предусмотрена', 'https://github.com/mlpack/mlpack'),
        'armadillo': ('no', 'Диагностика перекрытия отсутствует', 'https://gitlab.com/conradsnicta/armadillo-code'),
        'bnpy': ('partial', 'Расчет расстояний Кульбака-Лейблера и метрик сходства между компонентами', 'https://github.com/bnpy/bnpy'),
        'CAMAN': ('no', 'Метрики отделимости не предусмотрены', 'https://github.com/cran/CAMAN'),
    }
}

def main():
    # 1. Update requirements.csv
    req_file = BASE_DIR / "requirements.csv"
    with open(req_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        existing_reqs = list(reader)
        existing_req_ids = set(r["req_id"] for r in existing_reqs)
        fieldnames = reader.fieldnames

    reqs_to_add = [r for r in new_requirements if r["req_id"] not in existing_req_ids]
    if reqs_to_add:
        with open(req_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(reqs_to_add)
        print(f"Appended {len(reqs_to_add)} requirements to requirements.csv")
    else:
        print("No new requirements to add to requirements.csv")

    # 2. Update requirement_articles.csv
    req_art_file = BASE_DIR / "requirement_articles.csv"
    with open(req_art_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        existing_req_arts = set((r["req_id"], r["article_id"]) for r in reader)
        art_fieldnames = reader.fieldnames

    arts_to_add = []
    for req_id, aid, role, note in new_req_articles:
        if (req_id, aid) not in existing_req_arts:
            arts_to_add.append({
                "req_id": req_id,
                "article_id": aid,
                "role": role,
                "context_note": note
            })

    if arts_to_add:
        with open(req_art_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=art_fieldnames)
            writer.writerows(arts_to_add)
        print(f"Appended {len(arts_to_add)} links to requirement_articles.csv")
    else:
        print("No new links to add to requirement_articles.csv")

    # 3. Update evaluations.csv
    eval_file = BASE_DIR / "evaluations.csv"
    with open(eval_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        existing_evals = set((r["tool_id"], r["req_id"]) for r in reader)
        eval_fieldnames = reader.fieldnames

    evals_to_add = []
    for req_id, tools_dict in eval_data.items():
        for tool_id, (status, note, link) in tools_dict.items():
            if (tool_id, req_id) not in existing_evals:
                evals_to_add.append({
                    "tool_id": tool_id,
                    "req_id": req_id,
                    "status": status,
                    "evidence_note": note,
                    "evidence_link": link
                })

    if evals_to_add:
        with open(eval_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=eval_fieldnames)
            writer.writerows(evals_to_add)
        print(f"Appended {len(evals_to_add)} evaluations to evaluations.csv")
    else:
        print("No new evaluations to add to evaluations.csv")

if __name__ == "__main__":
    main()
