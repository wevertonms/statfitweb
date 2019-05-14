"""Cria o gráficos base da aplicação."""

import numpy as np
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Panel, Tabs, Range1d
from scipy import stats

from bokeh_models import Figure, colors

PARAMS_MAPPER = dict(
    norm=dict(loc=None, scale=None),
    lognorm=dict(s=None, loc=None, scale=None),
    weibull_min=dict(c=None, loc=None, scale=None),
    gamma=dict(a=None, loc=None, scale=None),
)


def cdf(hist, edges):
    """Cria um gráfico CDF (escada) com base no histograma.
    
    Args:
        hist (numpy.array): frequencias relativas do histograma.
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


class Plot:
    """Abstração para o gráficos base da aplicação."""

    def __init__(self):
        """Construtor."""
        self.values = []
        self.hist_source = ColumnDataSource(dict(x=[], y=[], left=[], right=[]))
        self.cumulative_source = ColumnDataSource(dict(x=[], y=[]))
        # Cria o plot base
        self.pdf_plot = Figure("Probability Density", ("Values", "Relative frequency"))
        self.pdf_plot.quad(
            source=self.hist_source,
            top="y",
            bottom=0,
            left="left",
            right="right",
            line_color="white",
            legend="Observed",
            color=colors[0],
        )
        self.cdf_plot = Figure(
            "Cumulative Probability",
            ("Values", "Relative frequency"),
            y_range=Range1d(start=0.0, end=1.02),
        )
        self.cdf_plot.line(
            source=self.cumulative_source,
            x="x",
            y="y",
            legend="Observed",
            line_width=2,
            color=colors[0],
        )
        self.pdf_source = {}
        self.cdf_source = {}
        for dist_name, color in zip(PARAMS_MAPPER.keys(), colors[1:]):
            legend = dist_name[0].upper() + dist_name[1:]
            self.pdf_source[dist_name] = ColumnDataSource(dict(x=[], y=[]))
            self.cdf_source[dist_name] = ColumnDataSource(dict(x=[], y=[]))
            line_opts = dict(legend=legend, line_width=3, color=color)
            self.pdf_plot.line(
                source=self.pdf_source[dist_name], x="x", y="y", **line_opts
            )
            self.cdf_plot.line(
                source=self.cdf_source[dist_name], x="x", y="y", **line_opts
            )

        self.pdf_plot.legend.click_policy = self.cdf_plot.legend.click_policy = "hide"
        self.pdf_plot.legend.location = self.cdf_plot.legend.location = "top_left"

        self.tabs = Tabs(
            tabs=[
                Panel(
                    child=layout(self.pdf_plot, sizing_mode="stretch_both"), title="PDF"
                ),
                Panel(
                    child=layout(self.cdf_plot, sizing_mode="stretch_both"), title="CDF"
                ),
            ]
        )

    def update_observed(self, num_bins, values=[]):
        """Função que atualiza o histograma e a CDF dos observações.
        
        Args:
            num_bins (int): número de intervalos para o histrograma.
        """
        if len(values) > 1:
            self.values = values
        hist, edges = np.histogram(self.values, density=True, bins=num_bins)
        self.cumulative_source.data["x"], self.cumulative_source.data["y"] = cdf(
            hist, edges
        )
        self.hist_source.data["left"] = edges[:-1]
        self.hist_source.data["right"] = edges[1:]
        x_ranges = [f"{l:.4g} - {r:.4g}" for l, r in zip(edges[:-1], edges[1:])]
        self.hist_source.data["x"] = x_ranges
        self.hist_source.data["y"] = hist

    def update_numeric(self):
        """Função que atualiza a PDF e a CDF dos ajustada."""
        for dist_name in PARAMS_MAPPER.keys():
            param = {}
            param[dist_name] = getattr(stats, dist_name).fit(self.values)
            for key, value in zip(PARAMS_MAPPER[dist_name].keys(), param[dist_name]):
                PARAMS_MAPPER[dist_name][key] = value
        x = np.linspace(min(self.values), max(self.values), len(self.values))
        for dist_name in PARAMS_MAPPER.keys():
            self.pdf_source[dist_name].data["x"] = x
            self.cdf_source[dist_name].data["x"] = x
            dist = getattr(stats, dist_name)(**PARAMS_MAPPER[dist_name])
            self.pdf_source[dist_name].data["y"] = dist.pdf(x)
            self.cdf_source[dist_name].data["y"] = dist.cdf(x)
