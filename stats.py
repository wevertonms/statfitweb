"""Módulo que implementa as análises estatísticas."""

import numpy as np
import scipy.stats as ss


class Dist:
    """Classe que associada a uma dada distribuição disponível na scipy.stats

    Args:
        name (str): nome da distribuição.
        scipy_class (scipy.stats.rvs): classe de scipy.stats associada com a distribuição.
        params (dict): dicionário com chaves equivalentes aos parâmetros de ajuste da distribuição.
    """

    def __init__(self, name, scipy_class, params_keys):
        """Construtor."""
        self.name = name
        self.scipy_class = scipy_class
        self.params_keys = params_keys
        self.pdf = None
        self.cdf = None

    def fit(self, observed_values):
        """Ajusta a distribuição para os valores das observações.

        Args:
            observed_values (numpy.array): valores das observações.
        """
        param_values = self.scipy_class.fit(observed_values)
        params = dict((k, v) for k, v in zip(self.params_keys, param_values))
        self.pdf = self.scipy_class(**params).pdf
        self.cdf = self.scipy_class(**params).cdf


DISTS = [
    Dist("Normal", ss.norm, ["loc", "scale"]),
    Dist("Log-Normal", ss.lognorm, ["s", "loc", "scale"]),
    Dist("Weibull", ss.weibull_min, ["c", "loc", "scale"]),
    Dist("Gamma", ss.gamma, ["a", "loc", "scale"]),
    Dist("Logistic", ss.logistic, ["loc", "scale"]),
]


def cumulative(hist, edges):
    """Cria um gráfico CDF (escada) com base no histograma.

    Args:
        hist (numpy.array): frequências relativas do histograma.
        edges (numpy.array): lista de valores que limitam as classes do histograma.

    Returns:
        list[float]: coordenadas do x dos pontos do gráfico.
        list[float]: coordenadas do y dos pontos do gráfico.
    """
    x = [edges[i // 2] for i in range(2 * len(edges[:-1]))]
    x.append(edges[-1])
    cdf = np.cumsum(hist * (edges[1] - edges[0]))
    y = [cdf[(i - 1) // 2] for i in range(2 * len(cdf))]
    y[0] = 0
    y.append(cdf[-1])
    return x, y


def chi_squared(values, cdf_function, num_bins):
    """Calcula o valor do teste Chi quadrado para um dado número de intervalos.

    Args:
        values (numpy.array): valores observados.
        cdf_function (callable): função que calcula a CDF para um dados pontos.
        num_bins (int): número de intervalos do histograma.

    Returns:
        float: p-value
    """
    hist, edges = np.histogram(values, density=True, bins=num_bins)
    observed = hist * (edges[1] - edges[0]) * len(values)
    expected = (cdf_function(edges)[1:] - cdf_function(edges)[:-1]) * len(values)
    results = ss.chisquare(observed, expected)
    return results[1]


def kolmogorov_smirnov(values, cdf_function):
    """Calcula o valor do teste Kolmogorov-Smirnov para um dado número de intervalos.

    Args:
        values (numpy.array): valores observados.
        cdf_function (callable): função que calcula a CDF para um dados pontos.

    Returns:
        float: p-value
    """
    return ss.kstest(values, cdf_function)[1]


def weverton(cdf, x, y):
    """Calcula o valor do teste Chi quadrado para um dado número de intervalos.

    Args:
        cdf_function (callable): função que calcula a CDF para um dados pontos.
        values (numpy.array): valores observados.
        num_bins (int): número de intervalos do histograma.

    Returns:
        float: valor do teste.
    """
    return np.sum((cdf(x) - y) ** 2)
