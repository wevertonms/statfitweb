import numpy as np
import scipy.stats as ss


class Dist:
    """Classe que associada a uma dada distribuição disponível na scipy.stats

    Args:
        name (str): nome da distribuição.
        scipy (scipy.stats.rvs): classe de scipy.stats associada com a distribuição.
        params (dict): dicionário com chaves equivalentes aos parâmetros de ajuste da distribuição.
    """

    def __init__(self, name, scipy, params):
        """Construtor."""
        self.name = name
        self.scipy = scipy
        self.params = params
        self.pdf = None
        self.cdf = None

    def fit(self, values):
        """Ajusta a distribuição para os valores das observações.

        Args:
            values (numpy.array): valores das observações
        """
        param = self.scipy.fit(values)
        for key, value in zip(self.params.keys(), param):
            self.params[key] = value
        self.pdf = self.scipy(**self.params).pdf
        self.cdf = self.scipy(**self.params).cdf


DISTS = [
    Dist("Normal", ss.norm, dict(loc=None, scale=None)),
    Dist("Log-Normal", ss.lognorm, dict(s=None, loc=None, scale=None)),
    Dist("Weibull", ss.weibull_min, dict(c=None, loc=None, scale=None)),
    Dist("Gamma", ss.gamma, dict(a=None, loc=None, scale=None)),
    Dist("Logistic", ss.logistic, dict(loc=None, scale=None)),
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


if __name__ == "__main__":
    values = np.linspace(-15, 15, 9)
    DISTS[0].fit(values)
    cdf_function = DISTS[0].cdf

    results = ss.kstest(values, cdf_function)
    print(f"KS: {results[0]:.3g}; p-value = {results[1]:.5g}")

    n_bins = np.random.randint(1, len(values))
    results = chi_squared(values, cdf_function, n_bins)
    print(f"Chi: {results[0]:.3g}; p-value = {results[1]:.5g} ({n_bins} bins)")
