"""Cria o gráficos base da aplicação."""

import numpy as np
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Panel, Tabs
from scipy import stats

from custom_figure import CustomFigure, colors

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
        self.observed_source = ColumnDataSource(
            dict(
                observed=[],
                x=[],
                cdf_x=[],
                cdf_y=[],
                cdf_quad_top=[],
                cdf_quad_left=[],
                cdf_quad_right=[],
            )
        )
        self.numeric_source = ColumnDataSource(dict(x=[]))
        # Cria o plot base
        self.pdf_plot = CustomFigure(
            "Probability Density", ("Values", "Relative frequency")
        )
        self.pdf_plot.quad(
            source=self.observed_source,
            top="cdf_quad_top",
            bottom=0,
            left="cdf_quad_left",
            right="cdf_quad_right",
            line_color="white",
            legend="Observed",
            color=colors[0],
        )
        self.cdf_plot = CustomFigure(
            "Cumulative Probability", ("Values", "Relative frequency")
        )
        self.cdf_plot.line(
            source=self.observed_source,
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
        if len(observed) < 1:
            observed = self.observed_source.data["observed"]
        x = np.linspace(min(observed), max(observed), len(observed))
        hist, edges = np.histogram(observed, density=True, bins=num_bins)
        cdf_x, cdf_y = cdf(hist, edges)
        self.observed_source.data.update(
            dict(
                observed=observed,
                x=x,
                cdf_x=cdf_x,
                cdf_y=cdf_y,
                cdf_quad_top=hist,
                cdf_quad_left=edges[:-1],
                cdf_quad_right=edges[1:],
            )
        )

    def update_numeric(self):
        """Função que atualiza a PDF e a CDF dos ajustada."""
        for dist_name in PARAMS_MAPPER.keys():
            param = {}
            param[dist_name] = getattr(stats, dist_name).fit(
                self.observed_source.data["observed"]
            )
            for key, value in zip(PARAMS_MAPPER[dist_name].keys(), param[dist_name]):
                PARAMS_MAPPER[dist_name][key] = value
        x = self.numeric_source.data["x"] = self.observed_source.data["x"]
        for dist_name in PARAMS_MAPPER.keys():
            dist = getattr(stats, dist_name)(**PARAMS_MAPPER[dist_name])
            data = {
                f"{dist_name}_pdf_y": dist.pdf(x),
                f"{dist_name}_cdf_y": dist.cdf(x),
            }
            self.numeric_source.data.update(data)
