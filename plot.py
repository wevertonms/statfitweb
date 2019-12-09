"""Cria o gráficos base da aplicação."""

import numpy as np
from bokeh.models import (
    ColumnDataSource,
    DataTable,
    NumberFormatter,
    Panel,
    TableColumn,
    Tabs,
)
from bokeh.palettes import Category10 as colors  # pylint:disable=no-name-in-module

from bokeh_models import Figure
from stats import cumulative

COLORS = colors[10]


class Plot:
    """Abstração para o gráficos base da aplicação."""

    def __init__(self, dists):
        """Construtor."""
        self.dists = dists
        self.values = []
        self.hist_source = ColumnDataSource(dict(x=[], y=[], left=[], right=[]))
        self.cumulative_source = ColumnDataSource(dict(x=[], y=[]))
        self.num_bins = 5
        # Cria o plot base
        self.pdf_plot = Figure("Probability Density", ("Values", "Relative frequency"))
        self.pdf_plot.quad(
            source=self.hist_source,
            top="y",
            bottom=0,
            left="left",
            right="right",
            line_color="white",
            legend_label="Observed",
            color=COLORS[0],
        )
        self.cdf_plot = Figure(
            "Cumulative Probability Density", ("Values", "Cumulative frequency")
        )
        self.cdf_plot.line(
            source=self.cumulative_source,
            x="x",
            y="y",
            legend_label="Observed",
            line_width=2,
            color=COLORS[0],
        )
        self.pdf_sources = {}
        self.cdf_sources = {}
        for dist, color in zip(dists, COLORS[1:]):
            self.pdf_sources[dist.name] = ColumnDataSource(dict(x=[], y=[]))
            self.cdf_sources[dist.name] = ColumnDataSource(dict(x=[], y=[]))
            line_opts = dict(legend_label=dist.name, line_width=3, color=color)
            self.pdf_plot.line(
                source=self.pdf_sources[dist.name], x="x", y="y", **line_opts
            )
            self.cdf_plot.line(
                source=self.cdf_sources[dist.name], x="x", y="y", **line_opts
            )
        self.pdf_plot.legend.click_policy = self.cdf_plot.legend.click_policy = "hide"
        self.pdf_plot.legend.location = self.cdf_plot.legend.location = "top_left"
        self.layout = Tabs(
            tabs=[
                Panel(child=self.pdf_plot, title="PDF"),
                Panel(child=self.cdf_plot, title="CDF"),
            ]
        )

    def update_histogram(self, hist, edges):
        """Função que atualiza o histograma das observações.

        Args:
            num_bins (int): número de intervalos para o histograma.
        """
        x_ranges = [f"{l:.4g} - {r:.4g}" for l, r in zip(edges[:-1], edges[1:])]
        self.hist_source.data.update(
            left=edges[:-1], right=edges[1:], x=x_ranges, y=hist
        )

    def update_data(self, values):
        """Função que atualiza os dados de observações.

        Args:
            values (numpy.array): valores das observações.
        """
        if len(values) <= 30:
            num_bins = 2 * np.sqrt(len(values))
        elif len(values) <= 100:
            num_bins = np.sqrt(len(values))
        else:
            num_bins = max(
                np.log(len(values)) + 1,  # Fórmula de Sturges
                3.5 * np.std(values) / (len(values) ** (1 / 3)),  # Fórmula de Scott
            )
        self.num_bins = int(num_bins)
        self.values = values
        hist, edges = np.histogram(self.values, density=True, bins=self.num_bins)
        self.update_histogram(hist, edges)
        hist, edges = np.histogram(self.values, density=True, bins=len(self.values))
        x, y = cumulative(hist, edges)
        self.cumulative_source.data = dict(x=x, y=y)
        #  Atualiza a PDF e a CDF dos ajustada.
        x = np.linspace(min(self.values), max(self.values), len(self.values))
        for dist in self.dists:
            dist.fit(self.values)
            self.pdf_sources[dist.name].data.update(x=x, y=dist.pdf(x))
            self.cdf_sources[dist.name].data.update(x=x, y=dist.cdf(x))


def fit_table(dist_names):
    """Tabela com os valores dos teste de aderencia para cada distribuição.

    Args:
        dist_names (list[str]): nomes das distribuição.
    """
    source = ColumnDataSource(
        dict(
            dist_names=dist_names,
            chi=[0] * len(dist_names),
            ks=[0] * len(dist_names),
            wms=[0] * len(dist_names),
        )
    )
    formatter = NumberFormatter(format="0.000", text_align="center")
    return DataTable(
        source=source,
        columns=[
            TableColumn(field="dist_names", title="Distribution"),
            TableColumn(field="chi", title="Chi", formatter=formatter),
            TableColumn(field="ks", title="KS", formatter=formatter),
            TableColumn(field="wms", title="WMS", formatter=formatter),
        ],
        width=300,
        index_position=None,
        fit_columns=True,
    )
