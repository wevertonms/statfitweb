"""Cria o gráficos base da aplicação."""

import numpy as np
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Panel, Range1d, Tabs
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

from bokeh_models import Figure, colors


def cumulative(hist, edges):
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
            legend="Observed",
            color=colors[0],
        )
        self.cdf_plot = Figure(
            "Cumulative Probability Density",
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
        self.pdf_sources = {}
        self.cdf_sources = {}
        for dist, color in zip(dists, colors[1:]):
            self.pdf_sources[dist.name] = ColumnDataSource(dict(x=[], y=[]))
            self.cdf_sources[dist.name] = ColumnDataSource(dict(x=[], y=[]))
            line_opts = dict(legend=dist.name, line_width=3, color=color)
            self.pdf_plot.line(
                source=self.pdf_sources[dist.name], x="x", y="y", **line_opts
            )
            self.cdf_plot.line(
                source=self.cdf_sources[dist.name], x="x", y="y", **line_opts
            )
        self.pdf_plot.legend.click_policy = self.cdf_plot.legend.click_policy = "hide"
        self.pdf_plot.legend.location = self.cdf_plot.legend.location = "top_left"
        # self.layout = layout(self.pdf_plot, self.cdf_plot, sizing_mode="stretch_both")
        self.layout = Tabs(
            tabs=[
                Panel(child=self.pdf_plot, title="PDF"),
                Panel(child=self.cdf_plot, title="CDF"),
            ]
        )

    def update_histogram(self, num_bins):
        """Função que atualiza o histograma e a CDF dos observações.
        
        Args:
            num_bins (int): número de intervalos para o histrograma.
        """
        hist, edges = np.histogram(self.values, density=True, bins=num_bins)
        x_ranges = [f"{l:.4g} - {r:.4g}" for l, r in zip(edges[:-1], edges[1:])]
        self.hist_source.data["left"] = edges[:-1]
        self.hist_source.data["right"] = edges[1:]
        self.hist_source.data["x"] = x_ranges
        self.hist_source.data["y"] = hist
        return hist, edges

    def update_data(self, values):
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
        self.update_histogram(self.num_bins)
        hist, edges = np.histogram(self.values, density=True, bins=len(self.values))
        x, y = cumulative(hist, edges)
        self.cumulative_source.data["x"] = x
        self.cumulative_source.data["y"] = y
        #  Atualiza a PDF e a CDF dos ajustada.
        for dist in self.dists:
            param = dist.scipy.fit(self.values)
            for key, value in zip(dist.params.keys(), param):
                dist.params[key] = value
        x = np.linspace(min(self.values), max(self.values), len(self.values))
        for dist in self.dists:
            self.pdf_sources[dist.name].data["x"] = x
            self.cdf_sources[dist.name].data["x"] = x
            dist.frozen = dist.scipy(**dist.params)
            self.pdf_sources[dist.name].data["y"] = dist.frozen.pdf(x)
            self.cdf_sources[dist.name].data["y"] = dist.frozen.cdf(x)


class Table:
    def __init__(self, dists):
        data = dict(
            dists=[dist.name for dist in dists],
            chi=[0] * len(dists),
            ks=[0] * len(dists),
            wms=[0] * len(dists),
        )
        self.source = ColumnDataSource(data)
        self.table = DataTable(
            source=self.source,
            columns=[
                TableColumn(field="dists", title="Distribution"),
                TableColumn(field="chi", title="Chi-squared"),
                TableColumn(field="ks", title="Kolmogorov-Smirnov"),
                TableColumn(field="wms", title="WMS"),
            ],
            width=400,
            index_position=None,
            fit_columns=True,
        )

