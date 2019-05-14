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
        self.observed = []
        self.observed_hist_source = ColumnDataSource(dict(top=[], left=[], right=[]))
        self.observed_cdf_source = ColumnDataSource(dict(cdf_x=[], cdf_y=[]))
        self.numeric_source = ColumnDataSource(dict(x=[]))
        # Cria o plot base
        self.pdf_plot = Figure(
            "Probability Density", ("Values", "Relative frequency")
        )
        self.pdf_plot.quad(
            source=self.observed_hist_source,
            top="top",
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
            source=self.observed_cdf_source,
            x="cdf_x",
            y="cdf_y",
            legend="Observed",
            line_width=2,
            color=colors[0],
        )
        for dist_name, color in zip(PARAMS_MAPPER.keys(), colors[1:]):
            pdf_name = f"{dist_name}_pdf_y"
            cdf_name = f"{dist_name}_cdf_y"
            legend = dist_name[0].upper() + dist_name[1:]
            self.numeric_source.data.update({pdf_name: [], cdf_name: []})
            line_opts = dict(legend=legend, line_width=2, color=color)
            self.pdf_plot.line(
                source=self.numeric_source, x="x", y=pdf_name, **line_opts
            )
            self.cdf_plot.line(
                source=self.numeric_source, x="x", y=cdf_name, **line_opts
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

    def update_observed(self, num_bins, observed=[]):
        """Função que atualiza o histograma e a CDF dos observações.
        
        Args:
            num_bins (int): número de intervalos para o histrograma.
        """
        if len(observed) > 1:
            self.observed = observed
        hist, edges = np.histogram(self.observed, density=True, bins=num_bins)
        cdf_x, cdf_y = cdf(hist, edges)
        self.observed_hist_source.data.update(
            dict(top=hist, left=edges[:-1], right=edges[1:])
        )
        self.observed_cdf_source.data.update(dict(cdf_x=cdf_x, cdf_y=cdf_y))
        x = np.linspace(min(self.observed), max(self.observed), len(self.observed))
        self.numeric_source.data["x"] = x

    def update_numeric(self):
        """Função que atualiza a PDF e a CDF dos ajustada."""
        for dist_name in PARAMS_MAPPER.keys():
            param = {}
            param[dist_name] = getattr(stats, dist_name).fit(self.observed)
            for key, value in zip(PARAMS_MAPPER[dist_name].keys(), param[dist_name]):
                PARAMS_MAPPER[dist_name][key] = value
        x = self.numeric_source.data["x"]
        for dist_name in PARAMS_MAPPER.keys():
            dist = getattr(stats, dist_name)(**PARAMS_MAPPER[dist_name])
            data = {
                f"{dist_name}_pdf_y": dist.pdf(x),
                f"{dist_name}_cdf_y": dist.cdf(x),
            }
            self.numeric_source.data.update(data)
